from pydantic import BaseModel, Field
from typing import Optional
from adversa_agentic_ai.prompts.responses.base_llm_response import BaseLlmResponse

class RedLlmResponse(BaseLlmResponse):
    next_action: Optional[str] = Field(..., description="The next action chosen from available_actions")
