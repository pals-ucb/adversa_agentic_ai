from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.agents import Agent
from ..stores.agent_store import AgentStore

router = APIRouter()
agent_db = AgentStore()

@router.post("/agents", response_model=Agent)
def create_agent(agent: Agent):
    if agent_db.get(agent.id):
        raise HTTPException(status_code=400, detail="Agent already exists")
    return agent_db.save(agent)

@router.get("/agents/{agent_id}", response_model=Agent)
def get_agent(agent_id: str):
    agent = agent_db.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/agents/{agent_id}", response_model=Agent)
def update_agent(agent_id: str, agent: Agent):
    if not agent_db.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_db.update(agent_id, agent)

@router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    if not agent_db.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    agent_db.delete(agent_id)
    return {"status": "deleted"}

@router.get("/agents", response_model=List[Agent])
def list_agents():
    return agent_db.list_all()
