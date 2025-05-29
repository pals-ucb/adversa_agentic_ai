# A simple Red Agent for getting started
from fastapi import FastAPI
from pydantic import BaseModel

from agents.base.llm_base_agent import LLMBaseAgent

class SimpleRedAgent(LLMBaseAgent):
    def build_prompt(self, context: str) -> str:
        return f"Analyze the following context for vulnerabilities: {context}"

# FastAPI app for interacting with agent
app = FastAPI()
agent = SimpleRedAgent(model_name="bedrock-anthropic", model_endpoint="aws::bedrock")
agent.connect()

@app.post("/agent/act")
def agent_act(payload: dict):
    context = payload.get("context", "")
    response = agent.action(context)
    return {"response": response}

@app.get("/agent/history")
def get_history():
    return agent.get_history()

@app.delete("/agent/history")
def clear_history():
    agent.history.clear()
    return {"message": "History cleared."}
