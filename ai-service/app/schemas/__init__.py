# backend/app/schemas/__init__.py

from .document import DocumentUploadResponse
from .ticket import (
    PriorityEnum,
    TicketGenerateRequest,
    GeneratedTicketData,
    TicketGenerateResponse,
)
# Add the new LLM schema
from .llm import AIProcessingResponse

__all__ = [
    "DocumentUploadResponse",
    "PriorityEnum",
    "TicketGenerateRequest",
    "GeneratedTicketData",
    "TicketGenerateResponse",
    "AIProcessingResponse",
]