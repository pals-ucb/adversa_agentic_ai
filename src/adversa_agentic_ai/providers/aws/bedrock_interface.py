# File: providers/aws/bedrock_interface.py

import logging
import json
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError

from adversa_agentic_ai.providers.adaptors.anthropic_claude_adaptor import AnthropicClaudeAdapter
from adversa_agentic_ai.providers.adaptors.cohere_command_adaptor import CohereCommandAdapter
from adversa_agentic_ai.providers.adaptors.llm_base_adaptor import BaseModelAdapter
from adversa_agentic_ai.config.config_manager import get_config_manager
from adversa_agentic_ai.utils.config_logger import get_agent_logger

logger = get_agent_logger()

MODEL_ADAPTER_REGISTRY = {
    "anthropic": AnthropicClaudeAdapter,
    "cohere": CohereCommandAdapter,
    # Add more adapters as needed
}

class BedrockLLMClient:
    def __init__(self):
        cfg = get_config_manager()
        self.region = cfg.get("providers", "aws", "platforms", "bedrock", "region")
        profile = cfg.get("providers", "aws", "credentials", "profile", default=None)

        # AWS session
        if profile:
            self.session = Session(profile_name=profile, region_name=self.region)
        else:
            self.session = Session(region_name=self.region)

        self.client = self.session.client("bedrock-runtime")
        self.model_id = None
        self.default_adapter: BaseModelAdapter = None

    def connect(self, model_id: str):
        self.model_id = model_id
        provider_key = self._extract_provider_key(model_id)
        adapter_factory = MODEL_ADAPTER_REGISTRY.get(provider_key)
        if not adapter_factory:
            raise ValueError(f"No adapter registered for model provider: '{provider_key}'")
        self.default_adapter = adapter_factory(self.model_id)
        logger.info(f"Bedrock client ready for model_id: {model_id} using adapter: {self.default_adapter.__class__.__name__}")
        try:
            # Simple test prompt
            ping = self.invoke(model_id, "Hello, 1+1=?")
            logger.info(f"Ping response from {model_id}: {ping!r}")
        except Exception as e:
            logger.exception("Ping failed.")
            raise RuntimeError("Bedrock ping test failed") from e

    def disconnect(self):
        self.model_id = None
        self.default_adapter = None
        logger.info("Disconnected from Bedrock LLM")

    def invoke(self, model_id: str, prompt: str, **kwargs) -> str:
        adapter = self._get_adapter_for_model(model_id)
        payload = adapter.format_prompt(prompt, **kwargs)
        logger.info(f"Payload: {payload} body: {json.dumps(payload)}")

        try:
            response = self.client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )

            response_body = json.loads(response["body"].read())
            logger.info(f"response: {response_body}")
            return adapter.extract_text(response_body)

        except (BotoCoreError, ClientError) as e:
            logger.exception("AWS Bedrock error")
            raise RuntimeError("LLM invocation failed") from e
        except Exception as e:
            logger.exception("Unexpected error invoking model")
            raise RuntimeError("LLM invocation failed") from e

    def _extract_provider_key(self, model_id: str) -> str:
        """
        Extracts the provider part of the model ID, e.g., 'anthropic.claude-v2:1' -> 'anthropic'
        """
        return model_id.split(".")[0].lower()

    def _get_adapter_for_model(self, model_id: str) -> BaseModelAdapter:
        if model_id == self.model_id and self.default_adapter:
            return self.default_adapter

        provider_key = self._extract_provider_key(model_id)
        adapter = MODEL_ADAPTER_REGISTRY.get(provider_key)
        if not adapter:
            raise ValueError(f"No adapter registered for model provider: '{provider_key}'")

        return adapter
