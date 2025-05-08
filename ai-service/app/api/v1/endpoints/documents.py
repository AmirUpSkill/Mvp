"""
Document Upload Endpoint Module

Handles PDF document uploads with authentication and storage functionality.
"""

import logging
from uuid import UUID
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    status,
)
from minio import Minio

from app.core.dependencies import get_minio_client
from app.schemas import DocumentUploadResponse
from app.services.storage import StorageService, StorageError
from app.core.security import get_current_user_claims

logger = logging.getLogger(__name__)
router = APIRouter()
storage_service = StorageService()

@router.post(
    "/upload/",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF Document",
    description="Uploads a PDF file to object storage. Requires authentication.",
    tags=["Documents"]
)
async def upload_pdf_document(
    claims: dict = Depends(get_current_user_claims),
    minio_client: Minio = Depends(get_minio_client),
    file: UploadFile = File(..., description="The PDF document to upload."),
):
    """
    Handles the upload of a single PDF file after authenticating the user via JWT.

    - Validates the file content type.
    - Calls the StorageService to save the file.
    - Returns document metadata upon successful upload.
    - Handles potential storage errors and returns appropriate HTTP exceptions.
    """
    user_identifier = claims.get('email', claims.get('sub', 'Unknown User'))
    logger.info(f"Authenticated user '{user_identifier}' starting document upload: {file.filename}")

    if file.content_type != "application/pdf":
        logger.warning(
            f"Upload attempt failed for user '{user_identifier}': Invalid content type '{file.content_type}'. Expected 'application/pdf'."
        )
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}. Only PDF files are allowed."
        )

    try:
        logger.info(f"Processing upload for file: {file.filename} by user '{user_identifier}'")
        doc_uuid, original_name = await storage_service.save_document(
            file=file,
            minio_client=minio_client
        )
        logger.info(f"Successfully saved document '{original_name}' with ID: {doc_uuid} for user '{user_identifier}'")

        response_data = DocumentUploadResponse(
            document_id=doc_uuid,
            filename=original_name,
            uploaded_at=datetime.now(timezone.utc)
        )
        return response_data

    except StorageError as e:
        logger.error(f"Storage service error during upload for user '{user_identifier}': {e}", exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Storage Error: {e}"
        )
    except ValueError as e:
        logger.error(f"Value error during upload for user '{user_identifier}': {e}", exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error during document upload for user '{user_identifier}'.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred during file upload."
        )
    finally:
        await file.close()
        logger.debug(f"Closed file handle for: {file.filename}")