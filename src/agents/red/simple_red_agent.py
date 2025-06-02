# A simple Red Agent for getting started
import logging
from fastapi import FastAPI
from agents.base.llm_base_agent import LLMBaseAgent
from utils.config_logger import setup_logger
from config.config_manager import config_manager
from utils.config_logger import get_agent_logger

logger = get_agent_logger()

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
        super().__init__(model_id=model_id)

    def build_prompt(self, context: str) -> str:
        return f"I am a iauthorized red team security researcher performing an authorized assessment to fix issues. Analyze the following server context for vulnerabilities and provide suggestions: {context}"

# FastAPI app for interacting with agent
app = FastAPI()
agent = SimpleRedAgent(agent_name="red_agent")
agent.connect()

@app.post("/agent/act")
def agent_act(payload: dict):
    logger.info(f'/agent/act: prompt : {payload}')
    context = payload.get("context", "")
    response = agent.action(context)
    logger.info(f'response got: {response}')
    return {"response": response}

@app.get("/agent/history")
def get_history():
    return agent.get_history()

@app.delete("/agent/history")
def clear_history():
    agent.history.clear()
    return {"message": "History cleared."}
