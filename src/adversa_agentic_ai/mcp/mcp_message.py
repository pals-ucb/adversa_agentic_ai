
# Message struct used to communicate between the Orchestrator, Agents, LLM


from typing import Dict, List, Any, Optional
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
    available_actions: Optional[List[str]] = None  # Optional override from Orchestrator
    history: List[Dict[str, Any]] = []  # [{"action": ..., "input": ..., "result": ..., "reward": ...}]

    def _format_observation(self) -> str:
        return json.dumps(self.observation, indent=2)

    def _format_actions(self) -> str:
        if not self.available_actions:
            return "None specified"
        return "\n".join(f"- {a}" for a in self.available_actions)

