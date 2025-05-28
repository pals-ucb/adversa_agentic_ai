from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class MCPMessage:
    role: str                         # "Red-E", "Blue-I", etc.
    goal: str                         # E.g., "Escalate privilege", "Find exposed credentials"
    step_count: int                   # Current simulation step
    observation: Dict                 # Full observation/state from the env
    history: List[str] = field(default_factory=list)   # History of prior interactions
    constraints: Optional[Dict] = None                 # Any agent-specific constraints
    hints: Optional[List[str]] = None                  # Optional UX/system hints

    def to_prompt(self) -> str:
        """Converts the message to a human-readable prompt."""
        history_str = "\n".join(self.history[-5:])  # last few items
        return f"""You are a {self.role} agent.
Your goal: {self.goal}
Current step: {self.step_count}
Environment Observation:
{self._format_observation()}

Recent interaction history:
{history_str}

Respond with your next best action.
"""
    
    def _format_observation(self) -> str:
        # You may expand this into a richer serialization
        return str(self.observation)
