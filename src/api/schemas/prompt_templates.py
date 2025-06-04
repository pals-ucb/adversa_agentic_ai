# File: src/api/schemas/prompt_templates.py

from pydantic import BaseModel
from typing import List, Optional

class PlaceholderSpec(BaseModel):
    name: str
    required: bool = True
    default: Optional[str] = None

class PromptTemplate(BaseModel):
    id: str
    name: str
    template: str
    description: Optional[str] = None
    placeholders: List[PlaceholderSpec] = []
