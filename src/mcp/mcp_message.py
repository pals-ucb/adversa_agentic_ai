
# Message struct used to communicate between the Orchestrator, Agents, LLM


from typing import Dict, Any, Optional
from pydantic import BaseModel
import json

class MCPMessage(BaseModel):
    role: str                                  # Agent role, e.g., "Planner", "Red", "Blue", "Inspector"
    goal: str
    event_count: int
    observation: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None
    role_description: Optional[str] = None
    action_description: Optional[str] = None
    prompt_template: Optional[str] = None

    def _format_observation(self) -> str:
        return json.dumps(self.observation, indent=2)
