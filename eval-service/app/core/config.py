import os
import logging
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = os.getenv("EVAL_SERVICE_APP_NAME", "Evaluation Service")

    EVAL_GOOGLE_API_KEY: str | None = None
    EVAL_AI_MODEL_NAME: str = "gemini-2.0-flash"
    EVAL_AI_TEMPERATURE: float = 0.2
    EVAL_AI_MAX_RETRIES: int = 2

    LOG_LEVEL: str = "INFO"

    # --- JWT Validation Settings --- 
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY" , "secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS512")
    JWT_ISSUER: Optional[str] = os.getenv("JWT_ISSUER", None)


settings = Settings()

# --- Startup Validation ---
if not settings.EVAL_GOOGLE_API_KEY:
    error_msg = "Critical Error: EVAL_GOOGLE_API_KEY is not set."
    logger.critical(error_msg)
    raise ValueError(error_msg)
else:
    logger.debug(f"EVAL_GOOGLE_API_KEY loaded.")

# Add validation check for JWT Secret
if settings.JWT_SECRET_KEY == "default_secret_change_this_eval" or not settings.JWT_SECRET_KEY:
    logger.warning("Security Warning: JWT_SECRET_KEY is not set or using a default placeholder in Eval Service!")
    # Depending on policy, you might raise an error here too if a real key is mandatory
    # raise ValueError("JWT_SECRET_KEY must be configured.")

logger.info(f"Evaluation Service settings loaded. Project Name: {settings.PROJECT_NAME}, Eval Model: {settings.EVAL_AI_MODEL_NAME}")