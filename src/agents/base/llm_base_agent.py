from fastapi import FastAPI
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4
from abc import ABC
from .agent_interface import AgentInterface
from providers.llm_factory import get_llm_client
import logging

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
    id: str
    prompt: str
    response: str
    relevancy: Optional[Relevancy] = None
    effectiveness: Optional[Effectiveness] = None
    rewarding: Optional[Rewarding] = None

class LLMBaseAgent(AgentInterface):
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.history: List[PromptHistoryEntry] = []
        self.connected = False
        self.llm_client = get_llm_client()
        self.logger = logging.getLogger("llm_agent")

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
        self.history.append(entry)
        self.logger.debug(f"Updated prompt history with entry: {entry.id}")

    def refine_history_for_prompt(self) -> List[PromptHistoryEntry]:
        return self.history

    def build_prompt(self, context: str) -> str:
        # To be implemented by subclass
        return context

    def action(self, context: str) -> str:
        if not self.connected:
            raise RuntimeError("Agent not connected to model")
        prompt = self.build_prompt(context)
        self.logger.info(f"Sending prompt to LLM: {prompt}")
        response = self.llm_client.invoke(self.model_id, prompt)
        self.logger.info(f"Received response from LLM {response}")
        entry = PromptHistoryEntry(
            id=str(uuid4()),
            prompt=prompt,
            response=response
        )
        self.update_history(entry)
        return response


