from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class PlatformType(str, Enum):
    bedrock = "bedrock"
    sagemaker = "sagemaker"
    openai = "openai"
    huggingface = "huggingface"
    azure_openai = "azure_openai"

class Platform(BaseModel):
    name: str
    type: PlatformType
    endpoint: Optional[str]
    region: Optional[str]
    cost_per_1k_tokens: Optional[float] = 0.0

class Provider(BaseModel):
    id: str
    name: str
    credentials_profile: str
    platforms: List[Platform]
