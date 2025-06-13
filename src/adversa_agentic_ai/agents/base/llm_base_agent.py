# Updated MCPMessage with action management and Base Agent with Enums and Tools
import re
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
from adversa_agentic_ai.config.config_manager import get_config_manager
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
                 max_tokens: int = 512):
        self.model_id = model_id
        self.history: List[PromptHistoryEntry] = []
        self.connected = False
        self.llm_client = get_llm_client(provider, platform)
        self.logger = get_agent_logger()
        self.conversational_memory = ConversationBufferMemory()
        self.summary_memory = []
        self.vector_memory: Optional[VectorStoreRetriever] = None
        self.tools: List[Tool] = []
        self.max_tokens = max_tokens
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
        template_str = message.prompt_template
        template = PromptTemplate.from_template(template_str)
        self.logger.debug(f'Final prompt template: {template}') 
        available_actions = list(message.available_actions) or [] 
        prompt_inputs  = {
            "role": message.role,
            "goal": message.goal,
            "role_description": message.role_description,
            "goal_description": message.goal_description,
            "event_count": message.event_count,
            "observation": message.observation,
            "constraints": message.constraints,
            "history": "\n".join(str(h) for h in message.history or []),
            "available_tools": "\n".join(tool.name for tool in self.tools) or "None",
            "available_actions": json.dumps(available_actions)
        }
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
        json_response = self.invoke_with_retry(prompt, retries=1, max_tokens=self.max_tokens)
        self.update_history({
            "prompt": prompt,
            "response": json.dumps(json_response)        })
        return json_response

    def invoke_with_retry(self, prompt: str, retries: int = 2, max_tokens: int = 512) -> Dict[str, Any]:
        for attempt in range(1, 1 + retries + 1):  # First try + `retries` and 1 more for range exclusivity.
            self.logger.info(f"Attempt {attempt}: invoking LLM with max_tokens={max_tokens}")
            raw_response = self.llm_client.invoke(self.model_id, prompt, max_tokens=max_tokens)
            cleaned = self._clean_llm_response(raw_response)
            if not self._is_json_truncated(cleaned):
                return json.loads(cleaned)
            self.logger.warning(f"Attempt {attempt} failed due to truncated JSON")
            max_tokens *= 2  # Double token limit
        raise RuntimeError("LLM response was invalid JSON after retries.")

    def _clean_llm_response(self, raw_response: str) -> Optional[str]:
        # Clean triple backtick-wrapped LLM response
        cleaned = re.sub(r"^```json|```$", "", raw_response.strip())
        cleaned = re.sub(r"^```|```$", "", cleaned.strip())
        return cleaned
    
    def _is_json_truncated(self, cleaned_json_str: str) -> bool:
        # Heuristic: unbalanced braces or ends abruptly
        try:
            json.loads(cleaned_json_str)
            return False
        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON detected: {e}")
            return True
