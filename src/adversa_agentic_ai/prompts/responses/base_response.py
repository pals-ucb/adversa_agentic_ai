from pydantic import BaseModel, Field
from typing import Optional

class BaseLlmResponse(BaseModel):
    suggested_action: str = Field(..., description="The action chosen from available_actions")
    best_action: str = Field(..., description="The best action possible when available_actions is limited in scope.")
    rationale: str = Field(..., description="Short justification for the choice")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    commentary: Optional[str] = Field(None, description="Optional extended reasoning")
