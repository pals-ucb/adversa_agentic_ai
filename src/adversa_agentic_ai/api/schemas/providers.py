from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class PlatformType(str, Enum):
    bedrock = "bedrock"                 # AWS Bedrock platform
    sagemaker = "sagemaker"             # AWS SageMaker inference endpoint
    openai = "openai"                   # OpenAI APIs (e.g., GPT-4)
    huggingface = "huggingface"         # Hugging Face Inference API or Hub
    azure_openai = "azure_openai"       # Azure-hosted OpenAI services

class Platform(BaseModel):
    name: str = Field(..., description="Name of the platform (e.g., 'gpt-4-bedrock', 'code-whisperer')")
    type: PlatformType = Field(..., description="Type of platform (AWS Bedrock, OpenAI, etc.)")
    endpoint: Optional[str] = Field(None, description="Endpoint URL for invoking the model (if applicable)")
    region: Optional[str] = Field(None, description="Cloud region where this platform is deployed")
    cost_per_1k_tokens: Optional[float] = Field(0.0, description="Estimated cost per 1,000 tokens (USD)")

class Provider(BaseModel):
    id: str = Field(..., description="Unique provider ID (e.g., 'aws-main', 'openai-team')")
    name: str = Field(..., description="Descriptive name of the provider organization or account")
    credentials_profile: str = Field(..., description="Named credentials profile for authentication (e.g., AWS profile)")
    platforms: List[Platform] = Field(..., description="List of platforms hosted or accessed by this provider")
