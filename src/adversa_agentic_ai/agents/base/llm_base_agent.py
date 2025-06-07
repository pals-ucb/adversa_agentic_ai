from dataclasses import dataclass, field
from fastapi import FastAPI
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from uuid import uuid4
from abc import ABC

from adversa_agentic_ai.mcp.mcp_message import MCPMessage
from .agent_interface import AgentInterface
from adversa_agentic_ai.providers.llm_factory import get_llm_client
import logging
from langchain_core.runnables import Runnable
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.prompts import PromptTemplate

# Enums for prompt metadata
class Relevancy(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class Effectiveness(str, Enum):
    effective = "effective"
    ineffective = "ineffective"

class Rewarding(str, Enum):
    yes = "yes"
    no = "no"

# Prompt History Entry
class PromptHistoryEntry(BaseModel):
    prompt: str
    response: str
    relevancy: Optional[Relevancy] = None
    effectiveness: Optional[Effectiveness] = None
    rewarding: Optional[Rewarding] = None
    id: str = field(default_factory=lambda: str(uuid4()))

class LLMBaseAgent(AgentInterface):
    def __init__(self, 
                 model_id: str, 
                 provider: str,
                 platform: str,
                 default_prompt_template: Optional[str] = None,
                 default_prompt_template_values: Optional[Dict[str,Any]] = None
                 ):
        self.model_id = model_id
        self.history: List[PromptHistoryEntry] = []
        self.connected = False
        self.llm_client = get_llm_client(provider, platform)
        self.logger = logging.getLogger("llm_agent")
        # Memory components
        self.conversational_memory = ConversationBufferMemory()
        self.summary_memory = []  # Could be summaries of past dialogues
        self.vector_memory: Optional[VectorStoreRetriever] = None
        # List of tools
        self.tools: List[Tool] = []
        self.default_prompt_template = default_prompt_template
        self.default_prompt_template_values = default_prompt_template_values

    def connect(self):
        self.llm_client.connect(model_id=self.model_id)
        self.connected = True
        self.logger.info(f"LLMBaseAgent connected to LLM provider: {self.model_id}")

    def disconnect(self):
        self.llm_client.disconnect()
        self.connected = False
        self.logger.info(f"LLMBaseAgent disconnected from LLM provider: {self.model_id}")

    def get_history(self) -> List[PromptHistoryEntry]:
        return self.history

    def update_history(self, entry: PromptHistoryEntry):
        entry = entry if isinstance(entry, PromptHistoryEntry) else PromptHistoryEntry(**entry)
        self.history.append(entry)
        self.logger.debug(f"Updated prompt history with entry: {entry.id}")

    def refine_history_for_prompt(self, observation: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Placeholder for filtering or summarizing relevant history
        return [vars(h) for h in self.history[-5:]]
    
    def build_prompt(self, message: MCPMessage) -> str:
        template_str = (
            message.prompt_template
            or self.default_prompt_template
            or "{role} | {goal} | {event_count} | {observation} | {history}"
        )
        template = PromptTemplate.from_template(template_str)
        prompt_inputs = {
            "role": message.role,
            "goal": message.goal,
            "event_count": message.event_count,
            "observation": message.observation,
            "history": "\n".join(message.history or [])
        }
        prompt_inputs.update(self.default_prompt_template_values)
        return template.format(**prompt_inputs)
    
    def register_tool(self, tool: Tool) -> None:
        self.tools.append(tool)
        self.logger.info(f"Registered tool: {tool.name}")

    def invoke(self, message: MCPMessage) -> Dict[str, Any]:
        if not self.connected:
            raise RuntimeError("Agent not connected")
        prompt = self.build_prompt(message)
        self.logger.debug(f"Prompt to LLM: {prompt}")
        response = self.llm_client.invoke(self.model_id, prompt)
        self.logger.debug(f"Response from LLM: {response}")
        self.update_history({
            "prompt": prompt,
            "response": response
        })
        return {"response": response}
