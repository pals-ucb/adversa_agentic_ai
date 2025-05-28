from agents.agent_interface import AgentInterface
from mcp.mcp_message import MCPMessage
from typing import List
import boto3
import json

class LLMAgent(AgentInterface):
    def __init__(self, agent_name: str, bedrock_model_id: str, context_window: int = 5):
        self.agent_name = agent_name
        self.bedrock_model_id = bedrock_model_id
        self.context_window = context_window
        self.history_buffer: List[str] = []
        self.client = None  # AWS Bedrock runtime client

    def connect(self):
        self.client = boto3.client("bedrock-runtime")

    def get_history_buffer(self) -> List[str]:
        return self.history_buffer[-self.context_window:]

    def refine_history(self, current_prompt: str) -> List[str]:
        # In this version, we use a simple fixed window. In future, use an LLM-based summarizer.
        return self.get_history_buffer()

    def generate_prompt(self, message: MCPMessage) -> str:
        return message.to_prompt()

    def prompt_llm(self, prompt: str) -> str:
        # Example assumes Anthropic Claude model on Bedrock
        body = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 300,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1.0,
            "stop_sequences": ["\n\nHuman:"]
        }

        response = self.client.invoke_model(
            body=json.dumps(body),
            modelId=self.bedrock_model_id,
            accept="application/json",
            contentType="application/json"
        )

        raw_output = json.loads(response["body"].read())
        reply = raw_output.get("completion", "")
        self.history_buffer.append(f"Prompt: {prompt}\nResponse: {reply}")
        return reply
