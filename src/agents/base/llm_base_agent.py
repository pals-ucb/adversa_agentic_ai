from fastapi import FastAPI
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4
from abc import ABC
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
    id: str
    prompt: str
    response: str
    relevancy: Optional[Relevancy] = None
    effectiveness: Optional[Effectiveness] = None
    rewarding: Optional[Rewarding] = None

# LLMBaseAgent implementing AgentInterface
class LLMBaseAgent(AgentInterface):
    def __init__(self, model_name: str, model_endpoint: str):
        self.model_name = model_name
        self.model_endpoint = model_endpoint
        self.history: List[PromptHistoryEntry] = []
        self.connected = False

    def connect(self):
        self.connected = True
        print(f"Connected to {self.model_name} at {self.model_endpoint}")

    def disconnect(self):
        self.connected = False
        print(f"Disconnected from {self.model_name}")

    def get_history(self) -> List[PromptHistoryEntry]:
        return self.history

    def update_history(self, entry: PromptHistoryEntry):
        self.history.append(entry)

    def refine_history_for_prompt(self) -> List[PromptHistoryEntry]:
        # Stub for now
        return self.history

    def build_prompt(self, context: str) -> str:
        raise NotImplementedError("build_prompt should be overridden by subclasses")

    def action(self, context: str) -> str:
        if not self.connected:
            raise RuntimeError("Agent not connected to model")

        prompt = self.build_prompt(context)
        response = f"[MockResponse for: {prompt}]"
        entry = PromptHistoryEntry(
            id=str(uuid4()),
            prompt=prompt,
            response=response
        )
        self.update_history(entry)
        return response

