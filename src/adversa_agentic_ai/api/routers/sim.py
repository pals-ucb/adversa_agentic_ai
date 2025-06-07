# File: src/api/routers/sim.py

from fastapi import APIRouter, HTTPException
from uuid import UUID
from ..schemas.sim import (
    SimRequest,
    SimResponse,
    SimStepRequest,
    SimStepResponse,
    SimStatus,
    SimStepDetail
)
from ..stores.sim_model_store import SimModelStore
from ..stores.sim_store import SimStore

router = APIRouter()

# Explicitly instantiate the store objects
sim_model_db = SimModelStore()
sim_runner_store = SimStore()

@router.post("/sim/model/load", response_model=SimResponse)
def load_sim_model(request: SimRequest):
    sim_model = sim_model_db.get(request.sim_model_id)
    if not sim_model:
        raise HTTPException(status_code=404, detail="SimModel not found")
    sim_id = sim_runner_store.load_sim_model(sim_model, step_mode=request.step_mode)
    return SimResponse(sim_id=sim_id, message="Simulation model loaded successfully")

@router.post("/sim/run", response_model=SimResponse)
def run_simulation(request: SimRequest):
    sim_model = sim_model_db.get(request.sim_model_id)
    if not sim_model:
        raise HTTPException(status_code=404, detail="SimModel not found")
    sim_id = sim_runner_store.run_simulation(sim_model)
    return SimResponse(sim_id=sim_id, message="Simulation run completed")

@router.post("/sim/step", response_model=SimStepResponse)
def step_simulation(request: SimStepRequest):
    result = sim_runner_store.step_simulation(request.sim_id)
    if not result:
        raise HTTPException(status_code=404, detail="Simulation step failed or not found")
    return result

@router.get("/sim/status/{sim_id}", response_model=SimStatus)
def get_simulation_status(sim_id: UUID):
    status = sim_runner_store.get_status(sim_id)
    if not status:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return status

@router.get("/sim/detail/{sim_id}", response_model=SimStepDetail)
def get_simulation_detail(sim_id: UUID):
    detail = sim_runner_store.get_latest_step_detail(sim_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Detail not found")
    return detail

@router.get("/sim/detail/{sim_id}/step/{step_index}", response_model=SimStepDetail)
def get_simulation_step_detail(sim_id: UUID, step_index: int):
    detail = sim_runner_store.get_step_detail(sim_id, step_index)
    if not detail:
        raise HTTPException(status_code=404, detail="Step detail not found")
    return detail
