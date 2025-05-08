import logging
import fitz
from uuid import UUID
from minio import Minio
from minio.error import S3Error
from starlette.concurrency import run_in_threadpool

class Settings:
    MINIO_BUCKET_NAME: str = "pdf-documents"

settings = Settings()

class ServiceError(Exception):
    pass

class DocumentNotFoundError(ServiceError):
    pass

class PDFParsingError(ServiceError):
    pass

logger = logging.getLogger(__name__)

def _fetch_object_bytes(minio_client: Minio, bucket_name: str, object_name: str) -> bytes:
    try:
        response = minio_client.get_object(bucket_name, object_name)
        pdf_bytes = response.read()
        return pdf_bytes
    finally:
        if 'response' in locals() and response:
            response.close()
            response.release_conn()

def _parse_pdf_bytes_with_fitz(pdf_bytes: bytes, document_id: UUID) -> str:
    try:
        text_parts = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc):
                page_text = page.get_text("text", sort=True).strip()
                if page_text:
                   text_parts.append(page_text)
        full_text = "\n\n---\n\n".join(text_parts)
        return full_text
    except Exception as e:
        raise PDFParsingError(f"Failed to parse PDF content for document {document_id}: {e}") from e

class PDFExtractorService:
    async def extract_text_from_document(
        self, document_id: UUID, minio_client: Minio
    ) -> str:
        bucket_name = settings.MINIO_BUCKET_NAME
        object_name = f"{document_id}.pdf"

        try:
            pdf_bytes = await run_in_threadpool(
                _fetch_object_bytes, minio_client, bucket_name, object_name
            )
            if not pdf_bytes:
                 return ""
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise DocumentNotFoundError(f"Document with ID {document_id} not found in storage.") from e
            else:
                raise ServiceError(f"Failed to retrieve document from storage: {e.code}") from e
        except Exception as e:
            raise ServiceError(f"An unexpected error occurred retrieving the document: {e}") from e

        try:
            full_text = await run_in_threadpool(
                _parse_pdf_bytes_with_fitz, pdf_bytes, document_id
            )
            return full_text

        except PDFParsingError as e:
             raise e
        except Exception as e:
            raise ServiceError(f"An unexpected error occurred during text extraction: {e}") from e
