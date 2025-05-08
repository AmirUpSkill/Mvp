"""
Configuration module for the AI Service application.

This module handles all configuration settings for the application, loading them from environment
variables with fallback default values. It uses pydantic_settings for settings management and
validation.

Settings include:
- API configuration
- MinIO object storage configuration
- File upload settings
- AI model parameters
- JWT authentication settings
"""

import os 
from typing import Optional, List 
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings class that manages all configuration parameters.
    Inherits from BaseSettings to support loading from environment variables.
    """
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Service"

    # MinIO Configuration
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "requirements-pdfs")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes
    ALLOWED_EXTENSIONS: List[str] = ["pdf"]

    # AI Model Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "gemini-2.0-flash")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", 0.9))
    AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", 2))

    # JWT Authentication Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS512")
    JWT_ISSUER: Optional[str] = os.getenv("JWT_ISSUER", None)

# Initialize settings instance
settings = Settings()

# Validate required environment variables
if not settings.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set. Please set it in the .env file.")