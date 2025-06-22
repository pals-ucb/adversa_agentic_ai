from ast import Pass
import os
from fastapi import APIRouter, HTTPException
from uuid import UUID
import requests
from httpx import get
from networkx import load_centrality
from ..schemas.sim import (
    SimModelLoadRequest,
    SimModelLoadResponse,
    SimRequest,
    SimResponse,
    SimStatus,
    SimStepDetail
)
from ..stores.sim_model_store import SimModelStore
from ..schemas.internal.orchestrator_schemas import (
    LoadModelRequest,
    LoadModelResponse
)
from adversa_agentic_ai.utils.config_logger import get_agent_logger
from adversa_agentic_ai.api.clients.orchestrator_client import OrchestrationClient

logger = get_agent_logger()

router = APIRouter(
    prefix="/sim",
    tags=["Simulation Runtime"],
    responses={404: {"description": "Simulation or model not found"}}
)

sim_model_db = SimModelStore()
orchestrator_client = OrchestrationClient()

@router.post(
    "/model/load",
    response_model=SimModelLoadResponse,
    summary="Load an adversa  model into memory and prepare for simulation",
    description="Loads an Adversa Model into memory and prepares it for execution. Optionally enables step-by-step mode."
)
def load_sim_model(request: SimModelLoadRequest):
    sim_model = sim_model_db.get(request.model_id)
    if not sim_model:
        raise HTTPException(status_code=404, detail="SimModel not found")
    try:
        load_req = LoadModelRequest(s3_bucket=sim_model_db.get_bucket_name(), 
                                    s3_path=sim_model_db.get_bucket_prefix(),
                                    model_id=request.model_id)
        resp = orchestrator_client.load_model(load_req)
        return SimModelLoadResponse(**resp.model_dump())
    except requests.HTTPError as e:
        logger.exception(f"Orchestrator HTTP error during model loading: {request.model_id}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json().get("detail", e.response.text)
        )
    except Exception as e:
        logger.exception(f"Unexpected error during Model load: {request.model_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post(
    "/run",
    response_model=SimResponse,
    summary="Run simulation to completion or one step at a time based on the mode",
    description="Executes the loaded SimModel simulation until it reaches a terminal state or just the next step."
)
def run_simulation(runSimRequest: SimRequest):
    try:
        resp = orchestrator_client.run_sim(runSimRequest)
        return SimResponse(**resp.model_dump()) 
    except requests.HTTPError as e:
        logger.exception(f"Orchestrator HTTP error during sim run: {runSimRequest.sim_id}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json().get("detail", e.response.text)
        )
    except Exception as e:
        logger.exception(f"Unexpected error during sim run: {runSimRequest.sim_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get(
    "/status/{sim_id}",
    response_model=SimStatus,
    summary="Get simulation status",
    description="Returns the current status (e.g., running, completed, error) of the simulation."
)
def get_simulation_status(sim_id: UUID):
    status = None
    if not status:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return status

@router.get(
    "/detail/{sim_id}",
    response_model=SimStepDetail,
    summary="Get latest simulation step detail",
    description="Retrieves details from the most recent simulation step."
)
def get_simulation_detail(sim_id: UUID):
    detail = None
    if not detail:
        raise HTTPException(status_code=404, detail="Detail not found")
    return detail

@router.get(
    "/detail/{sim_id}/step/{step_index}",
    response_model=SimStepDetail,
    summary="Get simulation step detail by index",
    description="Returns information about a specific simulation step based on the index provided."
)
def get_simulation_step_detail(sim_id: UUID, step_index: int):
    detail = None
    if not detail:
        raise HTTPException(status_code=404, detail="Step detail not found")
    return detail
