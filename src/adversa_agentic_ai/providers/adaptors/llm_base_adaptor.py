# providers/adaptors/llm_base_adaptor.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseModelAdapter(ABC):
    @abstractmethod
    def format_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Format the request payload given a prompt."""
        pass

    @abstractmethod
    def extract_text(self, response_body: Dict[str, Any]) -> str:
        """Extract the output text from the model's raw response."""
        pass
