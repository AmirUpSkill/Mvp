import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_v1_router

from fastapi import Request, Response
import logging


log_level_str = getattr(settings, 'LOG_LEVEL', 'INFO').upper() # Use getattr for safety
logging.basicConfig(level=getattr(logging, log_level_str, logging.INFO))
logger = logging.getLogger(__name__)

logger = logging.getLogger("ai-service")

logger.info(f"Initializing {settings.PROJECT_NAME}...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_headers_middleware(request: Request, call_next):
    # Log headers before processing request
    logger.info(f"Incoming Headers for {request.url.path}: {dict(request.headers)}")
    response = await call_next(request)
    return response

@app.get("/", tags=["Health Check"])
async def read_root():
    logger.debug("Root endpoint '/' accessed.")
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    logger.debug("Health endpoint '/health' accessed.")
    return {"status": "ok", "service": settings.PROJECT_NAME}

logger.info(f"Including API V1 router with prefix: {settings.API_V1_STR}")
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

logger.info(f"{settings.PROJECT_NAME} application startup complete.")
logger.info(f"OpenAPI docs available at: /docs")
