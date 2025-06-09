from abc import abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from langchain_core.runnables import Runnable

from adversa_agentic_ai.mcp.mcp_message import MCPMessage

# --- Agent Interface as a LangChain Runnable ---

class AgentInterface(Runnable):
    """
        Base interface for an LLM-driven agent that can connect, track memory, refine history,
        build prompts using prompt templates and MCPMessage, register tools, and invoke the LLM.
        Inherits from LangChain's Runnable interface.
    """

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
    def refine_history_for_prompt(self, observation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select and return a relevant subset of history for the next prompt
        based on current observation. This may involve summarization, prioritization,
        or filtering of relevant interaction context.
        """
        pass

    @abstractmethod
    def build_prompt(self, prompt_template: str, message: "MCPMessage") -> str:
        """
        Construct a prompt for the LLM using the given prompt template and MCPMessage.
        This allows for structured and configurable prompt construction.
        """
        pass

    @abstractmethod
    def invoke(self, message: MCPMessage) -> Dict[str, Any]:
        """
        Invoke the LLM using the current MCPMessage and return the structured action.
        This replaces the prior `action()` method for better clarity.
        """
        pass

    @abstractmethod
    def register_tool(self, tool: Any) -> None:
        """Register a new tool that can be used by the agent."""
        pass