# Updated MCPMessage with action management and Base Agent with Enums and Tools
from shlex import join
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import json
from abc import ABC, abstractmethod
from enum import Enum
from uuid import uuid4
from dataclasses import field
from langchain_core.runnables import Runnable
from langchain_core.tools import Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.prompts import PromptTemplate
from adversa_agentic_ai.utils.config_logger import get_agent_logger
from adversa_agentic_ai.mcp.mcp_message import MCPMessage
from adversa_agentic_ai.providers.llm_factory import get_llm_client
from .agent_interface import AgentInterface

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

# Clean this up and keep only generic actions.
class BaseActions(str, Enum):
    port_scan = "port_scan"
    email_phishing = "email_phishing"
    default_credentials_attempt = "default_credentials_attempt"

# Prompt History Entry
class PromptHistoryEntry(BaseModel):
    prompt: str
    response: str
    relevancy: Optional[Relevancy] = None
    effectiveness: Optional[Effectiveness] = None
    rewarding: Optional[Rewarding] = None
    id: str = field(default_factory=lambda: str(uuid4()))

# LLMBaseAgent
class LLMBaseAgent(AgentInterface, ABC):
    def __init__(self, 
                 model_id: str, 
                 provider: str,
                 platform: str,
                 default_prompt_template: Optional[str] = None,
                 default_prompt_template_values: Optional[Dict[str,Any]] = None):
        self.model_id = model_id
        self.history: List[PromptHistoryEntry] = []
        self.connected = False
        self.llm_client = get_llm_client(provider, platform)
        self.logger = get_agent_logger()
        self.conversational_memory = ConversationBufferMemory()
        self.summary_memory = []
        self.vector_memory: Optional[VectorStoreRetriever] = None
        self.tools: List[Tool] = []
        self.default_prompt_template = default_prompt_template
        self.default_prompt_template_values = default_prompt_template_values or {}
        self.connect()

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
        return [h.dict() for h in self.history[-5:]]

    def build_prompt(self, message: MCPMessage) -> str:
        template_str = (
            message.prompt_template
            or self.default_prompt_template
            or "{role} | {goal} | {event_count} | {observation} | {history} | {available_tools}"
        )
        if isinstance(template_str, PromptTemplate):
            template = template_str
        else:
            template = PromptTemplate.from_template(template_str)
        self.logger.debug(f'Final prompt template: {template}') 
        available_actions = list(self.get_combined_action_set(message))
        prompt_inputs = dict(self.default_prompt_template_values)
        prompt_inputs.update({
            "role": message.role,
            "goal": message.goal,
            "event_count": message.event_count,
            "observation": message.observation,
            "history": "\n".join(str(h) for h in message.history or []),
            "available_tools": "\n".join(tool.name for tool in self.tools) or "None",
            "available_actions": json.dumps(available_actions)
        })
        self.logger.debug(f"final prompt inputs: {prompt_inputs}")
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

    def get_base_actions(self) -> List[str]:
        return [e.value for e in BaseActions]

    @abstractmethod
    def get_agent_specific_actions(self) -> List[str]:
        pass

    def get_combined_action_set(self, mcp_msg: MCPMessage) -> List[str]:
        base = self.get_base_actions()
        specific = self.get_agent_specific_actions()
        orchestrator = mcp_msg.available_actions or []
        return sorted(set(base + specific + orchestrator))
