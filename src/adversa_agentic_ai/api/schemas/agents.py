from pydantic import BaseModel, Field
from typing import List, Optional

class Agent(BaseModel):
    id: str = Field(..., description="Unique identifier for the agent instance")
    name: str = Field(..., description="Human-readable name for the agent (e.g., 'RedAgentV1')")
    model_id: str = Field(..., description="ID of the model this agent is powered by (e.g., LLM or decision model)")
    provider: str = Field(..., description="Model provider or source (e.g., 'OpenAI', 'Anthropic', 'Local')")
    platform: str = Field(..., description="Hosting environment or execution platform (e.g., 'lambda', 'local', 'ecs')")
    host: str = Field(..., description="Hostname or IP address of the agent's serving endpoint")
    port: int = Field(..., description="Port on which the agent is exposed or reachable")
    tools: Optional[List[str]] = Field(default_factory=list, description="List of tools or plugins the agent can invoke (e.g., 'search', 'code-executor')")
    capabilities: Optional[List[str]] = Field(default_factory=list, description="Functional traits (e.g., 'recon', 'exploit', 'self-learn')")
    description: Optional[str] = Field(None, description="Optional longer description of the agent's purpose or behavior")
