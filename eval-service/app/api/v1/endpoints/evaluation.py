# eval-service/app/api/v1/endpoints/evaluation.py
import logging
from fastapi import (
    APIRouter,
    Depends,  # <<< Add Depends
    HTTPException,
    status,
)
from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas import EvaluateTicketRequest, EvaluateTicketResponse
from app.core.dependencies import get_evaluation_llm_model
from app.services.llm_evaluator import (
    LLMEvaluatorService,
    LLMEvaluationError,
    LLMResponseParsingError
)
from app.core.security import get_current_user_claims  # <<< Import the dependency

logger = logging.getLogger(__name__)
router = APIRouter()
llm_evaluator = LLMEvaluatorService()

@router.post(
    "/ticket",
    response_model=EvaluateTicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Generated Ticket JSON",
    description="...", # Keep your description
    tags=["Evaluation"],
    responses={ # <<< MAKE SURE THIS IS A DICTIONARY LIKE BELOW
        400: {"description": "Invalid request format (e.g., malformed JSON)."},
        422: {"description": "Evaluation LLM response parsing failed or input invalid."}, # Clarified 422
        500: {"description": "Internal server error during evaluation."},
        503: {"description": "Evaluation LLM service unavailable or failed."},
        # Add 401 if you forgot to handle SecurityException explicitly returning it, though 401 is often handled by FastAPI directly based on the dependency
        401: {"description": "Not authenticated - Invalid or missing JWT."}
    }
)
async def evaluate_ticket_endpoint(
    request_data: EvaluateTicketRequest,
    evaluation_llm: ChatGoogleGenerativeAI = Depends(get_evaluation_llm_model),
    claims: dict = Depends(get_current_user_claims)  # <<< ADD SECURITY DEPENDENCY
):
    """API endpoint to evaluate a generated ticket JSON using an LLM."""
    # Log user info from validated claims
    user_identifier = claims.get('email', claims.get('sub', 'UNKNOWN'))
    logger.info(f"User '{user_identifier}' initiated evaluation request.")
    logger.debug(f"Original system prompt snippet: {request_data.original_system_prompt[:100]}...")
    logger.debug(f"Generated JSON to evaluate: {request_data.generated_json}")

    try:
        is_valid, reasoning = await llm_evaluator.evaluate_ticket(
            generated_json=request_data.generated_json,
            original_system_prompt=request_data.original_system_prompt,
            evaluation_llm_client=evaluation_llm
        )
        response = EvaluateTicketResponse(
            is_valid=is_valid,
            evaluation_reasoning=reasoning
        )
        logger.info(f"Evaluation for user '{user_identifier}' completed. Verdict: {is_valid}")
        return response
    except LLMResponseParsingError as e:
        logger.error(f"Failed to parse evaluation LLM response for user '{user_identifier}': {e}", exc_info=True)
        raise HTTPException(...)
    except LLMEvaluationError as e:
        logger.error(f"Evaluation LLM invocation failed for user '{user_identifier}': {e}", exc_info=True)
        raise HTTPException(...)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error during ticket evaluation for user '{user_identifier}'.")
        raise HTTPException(...)