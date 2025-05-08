import logging
import json
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.llm import AIProcessingResponse
from app.schemas.ticket import GeneratedTicketData

class LLMConfigurationError(Exception):
    pass

class LLMProcessingError(Exception):
    pass

logger = logging.getLogger(__name__)

class LLMProcessorService:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            logger.critical("GOOGLE_API_KEY is missing. LLM Service cannot be initialized.")
            raise LLMConfigurationError("GOOGLE_API_KEY environment variable not set.")

        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.AI_MODEL_NAME,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=settings.AI_TEMPERATURE,
                convert_system_message_to_human=True
            )
            logger.info(f"LLM Processor Service initialized successfully with model: {settings.AI_MODEL_NAME}")
        except Exception as e:
            logger.exception(f"Failed to initialize ChatGoogleGenerativeAI: {e}")
            raise LLMConfigurationError(f"Failed to configure the LLM client: {e}") from e

    def _clean_json_string(self, raw_string: Optional[str]) -> Optional[str]:
        if raw_string is None:
            return None

        cleaned = raw_string.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[len("```json"):].strip()
        elif cleaned.startswith("```"):
             cleaned = cleaned[len("```"):].strip()

        if cleaned.endswith("```"):
            cleaned = cleaned[:-len("```")].strip()

        return cleaned

    async def generate_ticket_json(
        self,
        extracted_text: str,
        system_prompt: str
    ) -> AIProcessingResponse:
        logger.info("Starting LLM processing to generate ticket JSON...")
        raw_ai_output: Optional[str] = None
        cleaned_output: Optional[str] = None
        structured_output_dict: Optional[dict] = None
        validated_data: Optional[GeneratedTicketData] = None
        error_message: Optional[str] = None
        status = "error"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please process the following document content based on the instructions above:\n\n---\n\n{extracted_text}\n\n---")
        ]

        try:
            logger.debug(f"Invoking LLM model '{settings.AI_MODEL_NAME}' asynchronously...")
            response = await self.llm.ainvoke(messages)
            raw_ai_output = response.content

            if not raw_ai_output:
                 logger.warning("LLM returned an empty response.")
                 error_message = "LLM returned an empty response."

            else:
                logger.debug(f"Received raw response from LLM (length: {len(raw_ai_output)} chars)")
                cleaned_output = self._clean_json_string(raw_ai_output)
                if not cleaned_output:
                    logger.warning("LLM response content was empty after cleaning.")
                    error_message = "LLM response content was empty after cleaning."
                else:
                    try:
                        structured_output_dict = json.loads(cleaned_output)

                        try:
                            validated_data = GeneratedTicketData.model_validate(structured_output_dict)
                            status = "success"
                            logger.info("Successfully parsed and validated LLM output against GeneratedTicketData schema.")

                        except ValidationError as e:
                            logger.warning(f"LLM output parsed as JSON but failed Pydantic validation. Errors: {e.errors()}", exc_info=False)
                            error_message = f"LLM output is valid JSON but does not match the required schema. Validation Errors: {e.errors()}"

                        except Exception as e:
                            logger.exception(f"Unexpected error during Pydantic validation of LLM output.")
                            error_message = f"Unexpected error validating LLM output structure: {str(e)}"

                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse LLM response as JSON. Error: {e}", exc_info=False)
                        logger.warning(f"Cleaned LLM Output that failed parsing (start): {cleaned_output[:200]}...")
                        error_message = f"LLM response was not valid JSON. Parse Error: {e}. Cleaned output start: '{cleaned_output[:100]}...'"

        except Exception as e:
            logger.exception(f"Error during LLM model invocation or processing.")
            error_message = f"Failed during LLM interaction: {str(e)}"

        response_payload = AIProcessingResponse(
            status=status,
            ai_structured_output=validated_data,
            model_used=settings.AI_MODEL_NAME,
            error_message=error_message,
            raw_llm_output=raw_ai_output
        )

        return response_payload

try:
    llm_processor_service = LLMProcessorService()
except LLMConfigurationError as config_error:
    logger.critical(f"LLM Processor Service failed to initialize: {config_error}. LLM functionality will be unavailable.")
    llm_processor_service = None
