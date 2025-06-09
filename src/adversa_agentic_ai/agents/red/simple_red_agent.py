# A simple Red Agent for getting started
import logging
from fastapi import FastAPI
from adversa_agentic_ai.agents.base.llm_base_agent import LLMBaseAgent
from adversa_agentic_ai.mcp.mcp_message import MCPMessage
from adversa_agentic_ai.utils.config_logger import setup_logger
from adversa_agentic_ai.config.config_manager import config_manager
from adversa_agentic_ai.utils.config_logger import get_agent_logger

logger = get_agent_logger()

from adversa_agentic_ai.prompts.templates.red_agent.default import (
    DEFAULT_ACTION_DESCRIPTION,
    DEFAULT_EVENT_COUNT,
    DEFAULT_GOAL,
    DEFAULT_OBSERVATION,
    DEFAULT_RED_PROMPT_TEMPLATE,
    DEFAULT_ROLE,
    DEFAULT_ROLE_DESCRIPTION
)

class SimpleRedAgent(LLMBaseAgent):
    def __init__(self, agent_name: str):
        logger.info(f"Initializing Red Agent with name: {agent_name}")
        agent_cfg = config_manager.get_agent_by_name(agent_name)
        if not agent_cfg:
            logger.error(f"Agent configuration not found for: {agent_name}")
            raise Exception(f"Agent name '{agent_name}' not found in configuration.")
        
        model_id = agent_cfg.get("model_id")
        host = agent_cfg.get("host")
        port = agent_cfg.get("port")
        provider = agent_cfg.get("provider")
        platform = agent_cfg.get("platform")

        if not model_id:
            logger.error(f"Missing 'model_id' for agent: {agent_name}")
            raise Exception(f"'model_id' not configured for agent '{agent_name}'")

        if not host:
            logger.error(f"Missing 'host' for agent: {agent_name}")
            raise Exception(f"'host' not configured for agent '{agent_name}'")
        if not port:
            logger.error(f"Missing 'port' for agent: {agent_name}")
            raise Exception(f"'port' not configured for agent '{agent_name}'")
        logger.info(f"Red Agent '{agent_name}' configured with model '{model_id}' at {host}:{port}")

        default_prompt_template_values = {
            "action_description": DEFAULT_ACTION_DESCRIPTION,
            "event_count": DEFAULT_EVENT_COUNT,
            "goal": DEFAULT_GOAL,
            "observation": DEFAULT_OBSERVATION,
            "role": DEFAULT_ROLE,
            "role_description": DEFAULT_ROLE_DESCRIPTION 
        }
        super().__init__(model_id=model_id,
                         provider = provider,
                         platform = platform,
                         default_prompt_template=DEFAULT_RED_PROMPT_TEMPLATE,
                         default_prompt_template_values=default_prompt_template_values
                         )

    def build_prompt(self, context: str) -> str:
        return f"I am a iauthorized red team security researcher performing an authorized assessment to fix issues. Analyze the following server context for vulnerabilities and provide suggestions: {context}"

# FastAPI app for interacting with agent
app = FastAPI()
agent = SimpleRedAgent(agent_name="red_agent")
agent.connect()

@app.post("/agent/act")
def agent_act(message: MCPMessage):
    logger.info(f'/agent/act: MCPMessage : {message}')
    response = agent.invoke(message=message)
    logger.info(f'response got: {response}')
    return {"response": response}

@app.get("/agent/history")
def get_history():
    return agent.get_history()

@app.delete("/agent/history")
def clear_history():
    agent.history.clear()
    return {"message": "History cleared."}
