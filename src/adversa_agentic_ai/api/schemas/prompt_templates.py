from pydantic import BaseModel, Field
from typing import List, Optional

class PlaceholderSpec(BaseModel):
    name: str = Field(..., description="Name of the placeholder (e.g., 'user_name', 'query')")
    required: bool = Field(default=True, description="Whether this placeholder must be provided at runtime")
    default: Optional[str] = Field(None, description="Default value if not provided (optional)")

class PromptTemplate(BaseModel):
    id: str = Field(..., description="Unique ID of the prompt template")
    name: str = Field(..., description="Human-readable name or label for the prompt (e.g., 'greeting_template')")
    template: str = Field(..., description="Prompt text with placeholders (e.g., 'Hello {{user_name}}, how can I help?')")
    description: Optional[str] = Field(None, description="Optional explanation of what this prompt is used for")
    placeholders: List[PlaceholderSpec] = Field(default_factory=list, description="List of placeholders used in the template")
