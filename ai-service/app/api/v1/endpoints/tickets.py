# ai-service/app/api/v1/endpoints/tickets.py

import logging
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends, # <<< Import Depends
    HTTPException,
    status,
)
from minio import Minio

# --- Application Imports ---
# Schemas
from app.schemas import (
    TicketGenerateRequest,
    TicketGenerateResponse,
    AIProcessingResponse, # Assuming this is the response from llm_processor service
    GeneratedTicketData # The target validated data structure from llm_processor output
)
# Dependencies
from app.core.dependencies import get_minio_client
from app.core.security import get_current_user_claims # <<< Import the security dependency
# Services
from app.services.pdf_extractor import (
    PDFExtractorService,
    DocumentNotFoundError,
    PDFParsingError,
    ServiceError as ExtractorServiceError # Rename to avoid name clash if needed
)
from app.services.llm_processor import (
    llm_processor_service, # Using the singleton instance for POC
    LLMProcessingError,
    LLMConfigurationError # Import specific exceptions if needed
)

# --- Setup ---
logger = logging.getLogger(__name__)
router = APIRouter()
# Instantiate services (or inject if preferred)
pdf_extractor = PDFExtractorService()

# --- API Endpoint Definition ---
@router.post(
    "/generate-from-document",
    response_model=TicketGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Ticket from Document ID",
    description="Extracts text from a previously uploaded document and uses an LLM, "
                "guided by a system prompt, to generate a structured ticket. Requires authentication.",
    tags=["Tickets"],
    responses={
        401: {"description": "Authentication required or invalid token."},
        404: {"description": "Document not found in storage."},
        422: {"description": "Failed to parse PDF or LLM output validation failed."},
        500: {"description": "Internal server error during processing."},
        503: {"description": "Dependent service (Storage, LLM) unavailable or not configured."},
    }
)
async def generate_ticket_from_document(
    # Request body automatically validated
    request_data: TicketGenerateRequest,
    # Inject dependencies
    claims: dict = Depends(get_current_user_claims), # <<< ADD SECURITY DEPENDENCY
    minio_client: Minio = Depends(get_minio_client),
    # llm_service: LLMProcessorService = Depends(get_llm_processor_service) # Alternative if injecting service
):
    """
    Orchestrates the ticket generation pipeline after authenticating the user via JWT:
    1. Fetches and extracts text from the specified document ID using PDFExtractorService.
    2. Calls the LLMProcessorService with the extracted text and system prompt.
    3. Handles errors from each service appropriately.
    4. Returns the structured ticket data upon success.
    """
    document_id = request_data.document_id
    system_prompt = request_data.system_prompt
    user_identifier = claims.get('email', claims.get('sub', 'Unknown User'))
    logger.info(f"User '{user_identifier}' received request to generate ticket from document ID: {document_id}")

    # --- Step 1: Extract Text from PDF ---
    try:
        logger.info(f"Attempting text extraction for document: {document_id} by user '{user_identifier}'")
        extracted_text = await pdf_extractor.extract_text_from_document(
            document_id=document_id,
            minio_client=minio_client
        )
        if not extracted_text:
            logger.warning(f"Extraction yielded empty text for document: {document_id}. Processing will proceed but may be limited.")
        logger.info(f"Successfully extracted text (length: {len(extracted_text)}) for document: {document_id} by user '{user_identifier}'")

    except DocumentNotFoundError as e:
        logger.error(f"Document not found error for ID {document_id} requested by user '{user_identifier}': {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found in storage."
        )
    except PDFParsingError as e:
        logger.error(f"PDF parsing error for document {document_id} requested by user '{user_identifier}': {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse the PDF content for document '{document_id}'. It might be corrupted or invalid."
        )
    except ExtractorServiceError as e:
        logger.exception(f"Storage or other service error during text extraction for {document_id} requested by user '{user_identifier}'.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to retrieve or process document '{document_id}' due to a storage service issue: {e}"
        )
    except HTTPException as http_exc: # Re-raise HTTPExceptions from dependencies (like MinIO client init fail)
        raise http_exc
    except Exception as e:
         logger.exception(f"Unexpected error during text extraction phase for {document_id} requested by user '{user_identifier}'.")
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail="An unexpected error occurred during text extraction."
         )

    # --- Step 2: Process Text with LLM ---
    if llm_processor_service is None:
         logger.critical(f"LLM Processor Service is not available for request from user '{user_identifier}'.")
         raise HTTPException(
             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
             detail="AI processing service is not configured or available."
         )

    try:
        logger.info(f"Sending extracted text from document {document_id} to LLM Processor for user '{user_identifier}'.")
        # Assuming llm_processor_service.generate_ticket_json returns AIProcessingResponse schema instance
        ai_response: AIProcessingResponse = await llm_processor_service.generate_ticket_json(
            extracted_text=extracted_text,
            system_prompt=system_prompt
        )

        if ai_response.status == "error":
            logger.error(f"LLM processing failed for document {document_id} requested by user '{user_identifier}'. Error: {ai_response.error_message}")
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY # Default for processing/validation errors
            if "LLM interaction" in (ai_response.error_message or "") or "API error" in (ai_response.error_message or ""):
                 status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            raise HTTPException(
                status_code=status_code,
                detail=f"AI processing failed: {ai_response.error_message}"
            )

        if ai_response.ai_structured_output is None: # Should have GeneratedTicketData if status is success
             logger.error(f"LLM processing status was 'success' but structured output is missing for doc {document_id} requested by user '{user_identifier}'.")
             raise HTTPException(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail="AI processing succeeded but failed to provide structured output."
             )

        logger.info(f"Successfully generated structured ticket data for document: {document_id} for user '{user_identifier}'")

        # --- Step 3: Construct Final Successful Response ---
        final_response = TicketGenerateResponse(
            generated_json=ai_response.ai_structured_output, # Already validated GeneratedTicketData
            llm_raw_output=ai_response.raw_llm_output,
            document_id=document_id
        )
        return final_response

    except HTTPException as http_exc:
         raise http_exc # Re-raise known HTTP errors
    except LLMProcessingError as e: # Catch custom LLM errors if defined/used
        logger.exception(f"LLM processing error for {document_id} requested by user '{user_identifier}'.")
        raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail=f"An error occurred during AI processing: {e}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error during LLM processing phase for {document_id} requested by user '{user_identifier}'.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during AI processing."
        )