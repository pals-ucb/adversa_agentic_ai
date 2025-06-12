# File: providers/adaptors/anthropic_claude_adaptor.py

from adversa_agentic_ai.providers.adaptors.llm_base_adaptor import BaseModelAdapter
from typing import Any, Dict

class AnthropicClaudeAdapter(BaseModelAdapter):
    def __init__(self, model_id: str):
        pass
    def format_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return {
            "prompt": prompt,
            "max_tokens_to_sample": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "stop_sequences": kwargs.get("stop_sequences", ["\n\nHuman:"]),
            "anthropic_version": kwargs.get("anthropic_version", "bedrock-2023-06-01")
        }

    def extract_text(self, response_body: Dict[str, Any]) -> str:
        return response_body.get("completion", "")
