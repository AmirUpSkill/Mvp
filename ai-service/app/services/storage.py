import os 
import uuid 
from uuid import UUID
import logging 
from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
from starlette.concurrency import run_in_threadpool  

class Settings:
    """Configuration settings for MinIO storage"""
    MINIO_BUCKET_NAME: str = "pdf-documents"
    MINIO_PART_SIZE: int = 10 * 1024 * 1024  # 10MB part size for multipart uploads

settings = Settings()

class StorageError(Exception):
    """Custom exception for storage-related errors."""
    pass

logger = logging.getLogger(__name__)
class StorageService:
    """
    Service class for interacting with MinIO storage.
    """

    async def save_document(
        self, file: UploadFile, minio_client: Minio
    ) -> tuple[UUID, str]:
        """
        Saves an uploaded document (PDF) to the configured MinIO bucket.

        Args:
            file: The UploadFile object from the FastAPI request.
            minio_client: An initialized Minio client instance.

        Returns:
            A tuple containing the generated UUID for the stored object
            and the original filename.

        Raises:
            StorageError: If the bucket doesn't exist or if there's an error
                         during the upload process.
            ValueError: If the input file has no filename.
        """
        bucket_name = settings.MINIO_BUCKET_NAME 
        part_size = settings.MINIO_PART_SIZE

        if not file.filename:
            logger.error("Attempted to upload a file with no filename.")
            raise ValueError("Uploaded file has no filename.")
        
        # Verify if the MinIO bucket exists
        try:
            exists = await run_in_threadpool(minio_client.bucket_exists, bucket_name)
            if not exists:
                error_msg = (
                    f"MinIO bucket '{bucket_name}' does not exist. "
                    f"Please create it (e.g., via MinIO UI at http://localhost:9001)."
                )
                logger.error(error_msg)
                raise StorageError(error_msg)
        except S3Error as e:
            logger.exception(f"Error checking MinIO bucket: '{bucket_name}'")
            raise StorageError(f"Error checking MinIO bucket: {e}") from e
        except Exception as e:  # Handle unexpected errors like connection issues
            logger.exception(f"Unexpected error checking MinIO bucket '{bucket_name}'.")
            raise StorageError(f"Connection error or unexpected issue checking MinIO bucket: {e}") from e
        
        # let's generate Unique identifier 
        file_uuid = uuid.uuid4()
        # let's create Object Name Construction 
        _, extension = os.path.splitext(file.filename)
        object_name = f"{file_uuid}{extension.lower()}" # Ensure consistent extension casing
        # let's log upload attempt 
        logger.info(
            f"Attempting to upload file '{file.filename}' to bucket "  # Fixed string formatting
            f"'{bucket_name}' as object '{object_name}'"
        )

        # let's stream the file upload
        try: 
            await run_in_threadpool(
                minio_client.put_object,
                bucket_name=bucket_name,
                object_name=object_name,
                data=file.file,
                length=-1,
                content_type=file.content_type or "application/octet-stream",
                part_size=part_size,
            )
            logger.info(  
                f"Successfully uploaded '{file.filename}' as '{object_name}' "
                f"to bucket '{bucket_name}'"
            )

        # 5. Error Handling
        except S3Error as e:
            logger.exception(
                f"MinIO S3 Error uploading '{object_name}' to bucket '{bucket_name}'."
            )
            raise StorageError(f"Failed to upload document to MinIO: {e}") from e
        except Exception as e:
            # Catch other potential errors (network, etc.) during upload
            logger.exception(
                f"Unexpected error uploading '{object_name}' to bucket '{bucket_name}'."
            )
            raise StorageError(f"An unexpected error occurred during document upload: {e}") from e

        # 6. Return Value
        return file_uuid, file.filename
