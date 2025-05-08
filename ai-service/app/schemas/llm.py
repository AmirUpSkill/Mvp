from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from uuid import UUID

from .ticket import GeneratedTicketData

class AIProcessingResponse(BaseModel):
    """
    Schema for the response after processing content with the LLM.
    Contains the status, structured output (if successful), model info,
    raw output, and any errors.
    """
    status: str = Field(..., examples=["success", "error"], description="Indicates if the AI processing was successful.")
    ai_structured_output: Optional[GeneratedTicketData] = Field(
        None,
        description="The structured data extracted and validated against the GeneratedTicketData schema. Null if processing or validation failed."
    )
    model_used: str = Field(..., examples=["gemini-2.0-flash"], description="The identifier of the AI model used for generation.")
    error_message: Optional[str] = Field(None, description="Details about any error that occurred during processing or validation.")
    raw_llm_output: Optional[str] = Field(None, description="The raw string output received from the LLM before parsing/validation.")

    class Config:
        from_attributes = True