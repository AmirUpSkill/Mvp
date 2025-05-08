from pydantic import BaseModel, Field 
from datetime import datetime
from uuid import UUID

class DocumentUploadResponse(BaseModel):
    """
    Schema for the response after successfully uploading a document.
    
    Attributes:
        document_id (UUID): Unique identifier for the uploaded document
        filename (str): Name of the uploaded file
        uploaded_at (datetime): Timestamp when the document was uploaded
    """
    document_id: UUID = Field(
        ..., 
        description="Unique identifier for the document",
        example="f47ac10b-58cc-4372-a567-0e02b2c3d479"
    )
    filename: str = Field(
        ..., 
        description="Name of the uploaded file",
        example="user_requirements_v1.pdf"
    )
    uploaded_at: datetime = Field(
        ..., 
        description="Timestamp of when the document was uploaded",
        example="2023-10-19T14:30:00Z"
    )
