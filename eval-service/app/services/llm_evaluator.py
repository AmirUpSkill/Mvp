import logging
import json
from typing import Optional, Dict, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings

class LLMEvaluationError(Exception):
    pass

class LLMResponseParsingError(Exception):
    pass

logger = logging.getLogger(__name__)

INTERNAL_EVALUATION_PROMPT_TEMPLATE = """
You are an expert evaluator for AI-generated software requirement tickets.
Your task is to assess if the provided 'Generated JSON' accurately and adequately fulfills the requirements described in the 'Original System Prompt'.

**Evaluation Criteria:**
1.  **Schema Adherence:** Does the 'Generated JSON' strictly contain only the keys specified or implied by the 'Original System Prompt' (typically 'title', 'description', 'priority')? Are the data types correct (e.g., strings for title/description, allowed value for priority)?
2.  **Content Accuracy:** Does the 'title' concisely summarize the main requirement?
3.  **Content Completeness:** Does the 'description' capture the essential details, user story format, and acceptance criteria mentioned or requested in the 'Original System Prompt'? Is it comprehensive as requested?
4.  **Priority Correctness:** Is the 'priority' assigned logically based on keywords or instructions in the 'Original System Prompt'?

**Input:**
1.  **Original System Prompt:**
    ```
    {original_prompt}
    ```
2.  **Generated JSON:**
    ```json
    {generated_json_str}
    ```

**Output Format:**
Respond with ONLY the evaluation verdict followed by a colon and a brief explanation.
The verdict MUST be either "true" or "false".
Example format: `verdict: explanation`

**Example Output (if valid):**
`true: The generated JSON adheres to the required schema (title, description, priority), captures the core user story and acceptance criteria from the prompt, and assigns a logical priority.`

**Example Output (if invalid):**
`false: The 'priority' field contains an invalid value ('Urgent' instead of High/Medium/Low) and the description lacks the requested acceptance criteria details.`

**Now, evaluate the provided input based on the criteria and respond ONLY in the specified format.**
"""

class LLMEvaluatorService:
    async def evaluate_ticket(
        self,
        generated_json: Dict[str, Any],
        original_system_prompt: str,
        evaluation_llm_client: ChatGoogleGenerativeAI
    ) -> Tuple[bool, Optional[str]]:
        logger.info("Starting LLM-based evaluation...")

        try:
            generated_json_str = json.dumps(generated_json, indent=2)
        except Exception as e:
             logger.error(f"Failed to serialize generated_json for evaluation prompt: {e}")
             return False, f"Internal Error: Could not format the generated JSON for evaluation ({e})."

        final_evaluation_prompt = INTERNAL_EVALUATION_PROMPT_TEMPLATE.format(
            original_prompt=original_system_prompt,
            generated_json_str=generated_json_str
        )

        messages = [
            HumanMessage(content=final_evaluation_prompt)
        ]

        try:
            logger.debug(f"Invoking evaluation LLM: {evaluation_llm_client.model}")
            response = await evaluation_llm_client.ainvoke(messages)
            raw_eval_output = response.content.strip() if response and response.content else None
            logger.debug(f"Received raw response from evaluation LLM: '{raw_eval_output}'")

            if not raw_eval_output:
                logger.warning("Evaluation LLM returned an empty response.")
                raise LLMResponseParsingError("Evaluation LLM returned an empty response.")

        except Exception as e:
            logger.exception("Error occurred during evaluation LLM invocation.")
            raise LLMEvaluationError(f"Failed to get response from evaluation LLM: {e}") from e

        try:
            parts = raw_eval_output.split(':', 1)
            if len(parts) != 2:
                logger.warning(f"Evaluation LLM response did not match expected 'verdict: reasoning' format. Response: '{raw_eval_output}'")
                raise LLMResponseParsingError("Response format incorrect. Expected 'verdict: reasoning'.")

            verdict_str = parts[0].strip().lower()
            reasoning = parts[1].strip()

            if verdict_str == "true":
                is_valid = True
            elif verdict_str == "false":
                is_valid = False
            else:
                logger.warning(f"Evaluation LLM verdict ('{verdict_str}') is not 'true' or 'false'.")
                raise LLMResponseParsingError(f"Invalid verdict '{verdict_str}' received. Expected 'true' or 'false'.")

            logger.info(f"Evaluation completed. Verdict: {is_valid}. Reasoning: {reasoning}")
            return is_valid, reasoning

        except Exception as e:
            logger.exception("Error parsing the evaluation LLM's response.")
            raise LLMResponseParsingError(f"Failed to parse evaluation response '{raw_eval_output}': {e}") from e
