# providers/llm_factory.py

from config.config_manager import config_manager

# Import all available provider clients
from providers.aws.bedrock_interface import BedrockLLMClient

# provider client implies that it provides more than LLM client. We can get knowledgebase, Agents, Flows etc.
def get_llm_client():
    provider = config_manager.get("llm", "provider", default="bedrock")

    if provider == "bedrock":
        return BedrockLLMClient()
    
    raise ValueError(f"Unsupported LLM provider: {provider}")
