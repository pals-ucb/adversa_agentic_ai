# providers/aws/bedrock_interface.py

import boto3
import json
import logging
from botocore.exceptions import BotoCoreError, ClientError
from adversa_agentic_ai.config.config_manager import config_manager
from adversa_agentic_ai.utils.config_logger import get_agent_logger

logger = get_agent_logger()


class BedrockLLMClient:
    def __init__(self):
        self.region = config_manager.get("providers", "aws", "platforms", "bedrock", "region")
        self.temperature = config_manager.get("providers", "aws", "platforms", "bedrock", "temperature")
        self.max_tokens = config_manager.get("providers", "aws", "platforms", "bedrock", "max_tokens")
        self.client = None

    def _extract_bedrock_response(self, response: dict) -> str:
        try:
            body = response.get("body")
            if not body:
                return "[Response body missing]"
            decoded = body.read().decode("utf-8")
            try:
                parsed = json.loads(decoded)
                return (
                    parsed.get("completion")
                    or parsed.get("content")
                    or parsed.get("generation")
                    or json.dumps(parsed)  # fallback
                )
            except json.JSONDecodeError:
                return decoded  # plain string fallback

        except Exception as e:
            return f"[Error reading response body: {e}]"
        
    def connect(self, model_id):
        try:
            self.client = boto3.client("bedrock-runtime", region_name=self.region)
        except Exception as e:
            logger.exception("Failed to initialize Bedrock client")
            raise RuntimeError("Bedrock connection failed") from e

        # Send a lightweight ping/test prompt to verify LLM connection
        try:
            test_prompt = "\n\nHuman: Hello \n\nAssistant:"
            payload = {
                "prompt": test_prompt,
                "max_tokens_to_sample": 8,
                "stop_sequences": ["\n\nHuman:"]
            }
            response = self.client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                self.connected = True
                llm_msg = self._extract_bedrock_response(response)
                logger.info(f"Response received: {llm_msg}")
                logger.info(f"Connected to Bedrock model: {model_id}")
            else:
                raise RuntimeError(f"Unexpected status from Bedrock: {response['ResponseMetadata']}")
        except BotoCoreError as e:
            logger.error(f"Boto3 error while connecting to Bedrock: {e}")
            self.connected = False
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Bedrock: {e}")
            self.connected = False
            raise

    def disconnect(self):
        self.client = None
        logger.info("Disconnected from Bedrock")

    def invoke(self, model_id:str, prompt: str) -> str:
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
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            result = json.loads(response["body"].read())
            return result.get("completion", "[No completion received]")
        except (BotoCoreError, ClientError) as e:
            logger.exception("AWS error during Bedrock LLM call")
            raise RuntimeError("LLM invocation failed") from e
