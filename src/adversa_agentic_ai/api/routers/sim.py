from ast import Pass
import os
from fastapi import APIRouter, HTTPException
from uuid import UUID

from networkx import load_centrality
from ..schemas.sim import (
    SimRequest,
    SimResponse,
    SimStepRequest,
    SimStepResponse,
    SimStatus,
    SimStepDetail
)
from ..stores.sim_model_store import SimModelStore
from ..schemas.internal.orchestrator_schemas import (
    LoadModelRequest,
    LoadModelResponse
)
from adversa_agentic_ai.api.clients.orchestrator_client import OrchestrationClient

router = APIRouter(
    prefix="/sim",
    tags=["Simulation Runtime"],
    responses={404: {"description": "Simulation or model not found"}}
)

sim_model_db = SimModelStore()
orchestrator_client = OrchestrationClient()

@router.post(
    "/model/load",
    response_model=SimResponse,
    summary="Load a simulation model",
    description="Loads a SimModel into memory and prepares it for execution. Optionally enables step-by-step mode."
)
def load_sim_model(request: SimRequest):
    sim_model = sim_model_db.get(request.model_id)
    if not sim_model:
        raise HTTPException(status_code=404, detail="SimModel not found")
    load_req = LoadModelRequest(s3_bucket=sim_model_db.get_bucket_name(), 
                           s3_path=sim_model_db.get_bucket_prefix(),
                           model_id=request.model_id
                           )
    resp = orchestrator_client.load_model(load_req)
    return SimResponse(sim_id=resp.sim_id, status=resp.status)

@router.post(
    "/run",
    response_model=SimResponse,
    summary="Run simulation to completion",
    description="Executes the loaded SimModel simulation until it reaches a terminal state."
)
def run_simulation(request: SimRequest):
    sim_model = sim_model_db.get(request.sim_model_id)
    if not sim_model:
        raise HTTPException(status_code=404, detail="SimModel not found")
    sim_id = None
    return SimResponse(sim_id=sim_id, status="completed")

@router.post(
    "/step",
    response_model=SimStepResponse,
    summary="Run a single simulation step",
    description="Executes a single step in the step-by-step simulation mode."
)
def step_simulation(request: SimStepRequest):
    Pass

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
