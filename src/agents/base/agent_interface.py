from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AgentInterface(ABC):
    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the LLM or necessary backend services."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Clean up resources, close connections, etc."""
        pass

    @abstractmethod
    def get_history(self) -> List[Dict[str, Any]]:
        """Return the stored history of prompts and responses."""
        pass

    @abstractmethod
    def update_history(self, entry: Dict[str, Any]) -> None:
        """Update the internal history with a new entry."""
        pass

    @abstractmethod
    def refine_history_for_prompt(self) -> List[Dict[str, Any]]:
        """Select and return the relevant subset of history for the next prompt."""
        pass

    @abstractmethod
    def build_prompt(self, observation: Dict[str, Any]) -> str:
        """Construct a prompt for the LLM given the current observation and refined history."""
        pass

    @abstractmethod
    def action(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the LLM and return the structured action based on the observation."""
        pass
