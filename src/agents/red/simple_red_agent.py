# A simple Red Agent for getting started
import logging
from fastapi import FastAPI
from agents.base.llm_base_agent import LLMBaseAgent
from utils.config_logger import setup_logger

logger = logging.getLogger('red_agent')

class SimpleRedAgent(LLMBaseAgent):
    def build_prompt(self, context: str) -> str:
        return f"Analyze the following context for vulnerabilities: {context}"

# FastAPI app for interacting with agent
app = FastAPI()
agent = SimpleRedAgent(model_name="bedrock-anthropic", model_endpoint="aws::bedrock")
agent.connect()

@app.post("/agent/act")
def agent_act(payload: dict):
    print(f'promt) got: {payload}')
    logger.info(f'/agent/act: got message: {payload}')
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
