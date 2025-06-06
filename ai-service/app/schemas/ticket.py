from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID

class PriorityEnum(str, Enum):
    """Enumeration for ticket priority levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TicketGenerateRequest(BaseModel):
    """
    Schema for ticket generation request.
    
    Attributes:
        document_id (UUID): Unique identifier for the document to process
        system_prompt (str): Instructions for the LLM to extract ticket information
    """
    document_id: UUID = Field(
        ..., 
        example="f47ac10b-58cc-4372-a567-0e02b2c3d479",
        description="Unique identifier of the document to process"
    )
    system_prompt: str = Field(
        ...,
        example="Extract the main requirement title, a detailed description including acceptance criteria, and assign a priority (High, Medium, Low). Format as JSON with keys 'title', 'description', 'priority'.",
        description="Instructions for the LLM to extract ticket information"
    )

class GeneratedTicketData(BaseModel):
    """
    Schema for the structured ticket data.
    
    Attributes:
        title (str): Title of the ticket
        description (str): Detailed description including acceptance criteria
        priority (PriorityEnum): Priority level of the ticket
    """
    title: str = Field(
        ..., 
        example="Implement User Login via Email/Password",
        description="Title of the ticket"
    )
    description: str = Field(
        ...,
        example="As a user, I want to be able to log in using my registered email and password. AC: 1. Valid credentials log in. 2. Invalid credentials show error.",
        description="Detailed description including acceptance criteria"
    )
    priority: PriorityEnum = Field(
        ..., 
        example=PriorityEnum.HIGH,
        description="Priority level of the ticket"
    )

class TicketGenerateResponse(BaseModel):
    """
    Schema for ticket generation response.
    
    Attributes:
        generated_json (GeneratedTicketData): Structured ticket data generated by the LLM
        llm_raw_output (Optional[str]): Raw output from the LLM for debugging
        document_id (UUID): ID of the processed document
    """
    generated_json: GeneratedTicketData = Field(
        ...,
        description="The structured ticket data generated by the LLM, conforming to the GeneratedTicketData schema"
    )
    llm_raw_output: Optional[str] = Field(
        None,
        example='{\n  "title": "Implement User Login...",\n  "description": "As a user...",\n  "priority": "High"\n}',
        description="Optional: The raw string output received from the LLM, for debugging purposes"
    )
    document_id: UUID = Field(
        ...,
        example="f47ac10b-58cc-4372-a567-0e02b2c3d479",
        description="The ID of the document processed to generate this ticket"
    )
