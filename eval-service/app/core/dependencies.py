import logging
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi import HTTPException, status
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    if not settings.EVAL_GOOGLE_API_KEY:
        raise ValueError("EVAL_GOOGLE_API_KEY is missing in settings.")

    genai.configure(api_key=settings.EVAL_GOOGLE_API_KEY)
    logger.info("Evaluation Service: Google Generative AI SDK configured successfully with EVAL_GOOGLE_API_KEY.")

except ValueError as ve:
    logger.critical(f"Evaluation LLM Configuration Error: {ve}")
    raise ve
except Exception as e:
    logger.critical(f"CRITICAL: Error configuring Evaluation Google Generative AI SDK: {e}", exc_info=True)
    raise RuntimeError(f"Failed to configure Evaluation Google Generative AI SDK: {e}")

def get_evaluation_llm_model() -> ChatGoogleGenerativeAI:
    try:
        llm_model = ChatGoogleGenerativeAI(
            model=settings.EVAL_AI_MODEL_NAME,
            temperature=settings.EVAL_AI_TEMPERATURE,
            google_api_key=settings.EVAL_GOOGLE_API_KEY
        )
        logger.debug(f"Providing Evaluation LLM client instance for model: {settings.EVAL_AI_MODEL_NAME}")
        return llm_model

    except Exception as e:
        logger.exception(f"Failed to create Evaluation LLM client instance (model: {settings.EVAL_AI_MODEL_NAME}).")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not initialize the evaluation AI model instance: {e}"
        )
