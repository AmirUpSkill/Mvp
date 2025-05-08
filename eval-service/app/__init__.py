import logging
import uvicorn
from fastapi import FastAPI
from app.core.config import settings

log_level_str = settings.LOG_LEVEL.upper()
logging.basicConfig(level=getattr(logging, log_level_str, logging.INFO))
logger = logging.getLogger(__name__)

logger.info("Initializing Evaluation Service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/", tags=["Health Check"])
async def read_root():
    logger.debug("Root endpoint '/' accessed.")
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    logger.debug("Health endpoint '/health' accessed.")
    return {"status": "ok", "service": settings.PROJECT_NAME}

logger.info(f"{settings.PROJECT_NAME} application startup complete.")
logger.info(f"OpenAPI docs available at: /docs")
