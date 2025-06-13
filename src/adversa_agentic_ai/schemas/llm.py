import logging
from typing import List
from pydantic import BaseModel, Field, RootModel, ValidationError
from typing import List, Optional, Any
from adversa_agentic_ai.utils.config_logger import get_agent_logger
import logging

logger = get_agent_logger()

class BaseLlmResponse(BaseModel):
    suggested_action: str = Field(..., description="The action chosen from available_actions")
    best_action: str = Field(..., description="The best action possible when available_actions is limited in scope.")
    rationale: str = Field(..., description="Short justification for the choice")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    commentary: Optional[str] = Field(None, description="Optional extended reasoning")

class BaseLlmListResponse(RootModel[List[BaseLlmResponse]]):
    pass


def parse_and_validate_llm_response(raw_json: Any) -> BaseLlmListResponse:
    """
    Parses and validates an LLM response into BaseLlmListResponse.
    Raises ValueError if invalid or missing required fields.
    """
    try:
        parsed = BaseLlmListResponse.model_validate(raw_json)
    except ValidationError as e:
        logger.error(f"Pydantic validation failed: {e}")
        raise ValueError("LLM response structure is invalid")

    # Additional semantic checks on required keys and value ranges (if needed)
    for idx, action in enumerate(parsed.root):
        if not (0.0 <= action.confidence <= 1.0):
            raise ValueError(f"Invalid confidence at index {idx}: {action.confidence}")
        if not action.suggested_action or not action.best_action:
            raise ValueError(f"Missing required action fields at index {idx}")

    return parsed
