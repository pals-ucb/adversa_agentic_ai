# providers/llm_factory.py

from config.config_manager import config_manager

# Import all available provider clients
from providers.aws.bedrock_interface import BedrockLLMClient

# provider client implies that it provides more than LLM client. We can get knowledgebase, Agents, Flows etc.
def get_llm_client():
    default_provider  = config_manager.get("providers", "default", "provider", default="aws")
    default_platform = config_manager.get("providers", "default", "platform", default="aws")

    if default_provider == "aws" and default_platform == "bedrock":
        return BedrockLLMClient()
    
    raise ValueError(f"Unsupported LLM provider: {default_provider} platform: {default_platform}")
