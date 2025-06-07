from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.agents import Agent
from ..stores.agent_store import AgentStore

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    responses={404: {"description": "Agent not found"}}
)

agent_db = AgentStore()

@router.post("/", response_model=Agent, summary="Create a new agent", description="Registers a new agent with the specified ID and configuration.")
def create_agent(agent: Agent):
    if agent_db.get(agent.id):
        raise HTTPException(status_code=400, detail="Agent already exists")
    return agent_db.save(agent)

@router.get("/{agent_id}", response_model=Agent, summary="Retrieve agent details", description="Fetches the details of a registered agent by its ID.")
def get_agent(agent_id: str):
    agent = agent_db.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=Agent, summary="Update an existing agent", description="Updates the metadata or configuration of an existing agent.")
def update_agent(agent_id: str, agent: Agent):
    if not agent_db.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_db.update(agent_id, agent)

@router.delete("/{agent_id}", summary="Delete an agent", description="Deletes the specified agent from the registry.")
def delete_agent(agent_id: str):
    if not agent_db.get(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    agent_db.delete(agent_id)
    return {"status": "deleted"}

@router.get("/", response_model=List[Agent], summary="List all agents", description="Returns a list of all registered agents.")
def list_agents():
    return agent_db.list_all()
