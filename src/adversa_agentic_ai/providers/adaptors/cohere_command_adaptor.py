# cohere_command_adaptor.py
from adversa_agentic_ai.providers.adaptors.llm_base_adaptor import BaseModelAdapter
from typing import Any, Dict
import re

MODEL_CONFIG = {
    "cohere.command-text-v14": {
        "input_key": "prompt",
        "supports_stop_sequences": True,
        "supports_chat_history": False,
        "output_key": "generations.0.text"
    },
    "cohere.command-r-plus-v1": {
        "input_key": "message",
        "supports_stop_sequences": False,
        "supports_chat_history": True,
        "output_key": "text"
    },
    "cohere.command-r-v1": {
        "input_key": "message",
        "supports_stop_sequences": False,
        "supports_chat_history": True,
        "output_key": "text"
    },
}

class CohereCommandAdapter(BaseModelAdapter):
    def __init__(self, model_id: str):
        self.model_id = model_id
        self._config = self._resolve_config(model_id)

    def _resolve_config(self, model_id: str) -> Dict[str, Any]:
        # Normalize by stripping version suffix like :0
        base_id = re.sub(r":\d+$", "", model_id.strip().lower())
        return MODEL_CONFIG.get(base_id, {
            "input_key": "prompt",
            "supports_stop_sequences": True,
            "supports_chat_history": False,
            "output_key": "generations.0.text"
        })

    def format_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        body = {
            self._config["input_key"]: prompt,
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.5),
            "p": kwargs.get("top_p", kwargs.get("p", 0.9)),
            "k": kwargs.get("top_k", kwargs.get("k", 0)),
        }
        if self._config["supports_stop_sequences"]:
            body["stop_sequences"] = kwargs.get("stop_sequences", [])
        if self._config["supports_chat_history"] and "chat_history" in kwargs:
            body["chat_history"] = kwargs["chat_history"]
        return body

    def extract_text(self, response_body: Dict[str, Any]) -> str:
        path = self._config["output_key"].split(".")
        value = response_body
        for key in path:
            if key.isdigit():
                index = int(key)
                if isinstance(value, list) and len(value) > index:
                    value = value[index]
                else:
                    return ""
            else:
                value = value.get(key, "")
        return value if isinstance(value, str) else ""
