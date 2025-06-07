from pydantic import BaseModel, Field
from typing import List, Optional

class Agent(BaseModel):
    id: str
    name: str
    model_id: str
    provider: str
    platform: str
    host: str
    port: int
    tools: Optional[List[str]] = []
    capabilities: Optional[List[str]] = []
    description: Optional[str] = None
