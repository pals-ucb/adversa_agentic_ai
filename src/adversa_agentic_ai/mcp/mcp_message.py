
# Message struct used to communicate between the Orchestrator, Agents, LLM


from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json

class MCPMessage(BaseModel):
    role: str                                  # Agent role, e.g., "Planner", "Red", "Blue", "Inspector"
    role_description: str
    goal: str
    goal_description: str
    event_count: int
    observation: Dict[str, Any]
    prompt_template: str    
    available_actions: List[str] = None  # Optional list of actions 
    history: Optional[List[Dict[str, Any]]] = []  # [{"action": ..., "input": ..., "result": ..., "reward": ...}]
    constraints: Optional[Dict[str, Any]] = None
    available_tools: Optional[List[str]] = None  # Optional list of tools

    def _format_observation(self) -> str:
        return json.dumps(self.observation, indent=2)

    def _format_actions(self) -> str:
        if not self.available_actions:
            return "None specified"
        return "\n".join(f"- {a}" for a in self.available_actions)

