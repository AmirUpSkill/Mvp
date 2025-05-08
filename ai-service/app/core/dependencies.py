from minio import Minio 
import google.generativeai as genai 
from google.generativeai import GenerativeModel
from fastapi import HTTPException, status, Depends
from app.core.config import settings 

"""
Dependencies module for handling external service connections and configurations.

This module provides dependency injection functions for:
- Google Generative AI (Gemini) configuration and model instantiation
- MinIO client connection for object storage
"""

# Configure Google Generative AI SDK
try:
    if not settings.GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is not set in the environment variables."
        )
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    print("Google Generative AI SDK configured successfully.")

except ValueError as ve:
    print(f"Configuration Error: {ve}")
    raise ve

except Exception as e:
    print(f"Error configuration Google Generative AI SDK: {e}")
    raise RuntimeError(f"Failed to configure Google Generative AI SDK: {e}")

def get_minio_client() -> Minio:
    """
    Creates and returns a MinIO client instance.
    
    Returns:
        Minio: Configured MinIO client instance
        
    Raises:
        HTTPException: If connection to MinIO fails
    """
    try: 
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        print(f"MinIO client created for endpoint: {settings.MINIO_ENDPOINT}")
        return minio_client

    except Exception as e:
        print(f"Error creating MinIO client: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to MinIO storage: {e}"
        )

def get_gemini_model() -> GenerativeModel:
    """
    Creates and returns a Gemini model instance.
    
    Returns:
        GenerativeModel: Configured Gemini model instance
        
    Raises:
        HTTPException: If model instantiation fails
    """
    try:
        model = genai.GenerativeModel(settings.AI_MODEL_NAME)
        print(f"Gemini Model instance created for model: {settings.AI_MODEL_NAME}")
        return model

    except Exception as e:
        print(f"Error creating Gemini Model instance: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not instantiate Gemini Model: {e}"
        )