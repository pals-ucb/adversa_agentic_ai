# providers/aws/bedrock_interface.py

import boto3
import json
import logging
from botocore.exceptions import BotoCoreError, ClientError
from config.config_manager import config_manager

logger = logging.getLogger("bedrock")

class BedrockLLMClient:
    def __init__(self):
        self.region = config_manager.get("aws", "bedrock", "region")
        self.model_id = config_manager.get("aws", "bedrock", "model_id")
        self.temperature = config_manager.get("aws", "bedrock", "temperature")
        self.max_tokens = config_manager.get("aws", "bedrock", "max_tokens")
        self.client = None

    def connect(self):
        try:
            self.client = boto3.client("bedrock-runtime", region_name=self.region)
            logger.info(f"Connected to Bedrock model: {self.model_id} in region: {self.region}")
        except Exception as e:
            logger.exception("Failed to initialize Bedrock client")
            raise RuntimeError("Bedrock connection failed") from e

    def disconnect(self):
        self.client = None
        logger.info("Disconnected from Bedrock")

    def invoke(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("Bedrock client is not connected")

        body = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": self.max_tokens,
            "temperature": self.temperature,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman:"]
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            result = json.loads(response["body"].read())
            return result.get("completion", "[No completion received]")
        except (BotoCoreError, ClientError) as e:
            logger.exception("AWS error during Bedrock LLM call")
            raise RuntimeError("LLM invocation failed") from e
