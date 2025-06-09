# providers/llm_factory.py

from adversa_agentic_ai.config.config_manager import config_manager

# Import all available provider clients
from adversa_agentic_ai.providers.aws.bedrock_interface import BedrockLLMClient

# provider client implies that it provides more than LLM client. We can get knowledgebase, Agents, Flows etc.
def get_llm_client(provider: str, platform: str):
    if provider == "aws" and platform == "bedrock":
        return BedrockLLMClient()
    
    raise ValueError(f"Unsupported LLM provider: {provider} platform: {platform}")
