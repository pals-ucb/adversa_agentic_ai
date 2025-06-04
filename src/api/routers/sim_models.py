# File: src/api/routers/sim_models.py

from fastapi import APIRouter, HTTPException
from utils.config_logger import get_agent_logger
from typing import List
from ..schemas.sim_models import (
    SimModel
)
from ..stores.sim_model_store import SimModelStore

logger = get_agent_logger()
router = APIRouter()
sim_model_db = SimModelStore()

@router.post("/sim/models", response_model=SimModel)
def create_sim_model(model: SimModel):
    logger.info(f'SimModel: create {model}')
    if sim_model_db.get(model.id):
        raise HTTPException(status_code=400, detail="Model already exists")
    return sim_model_db.save(model)

@router.get("/sim/models/{model_id}", response_model=SimModel)
def get_sim_model(model_id: str):
    model = sim_model_db.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.put("/sim/models/{model_id}", response_model=SimModel)
def update_sim_model(model_id: str, updated_model: SimModel):
    if not sim_model_db.get(model_id):
        raise HTTPException(status_code=404, detail="Model not found")
    return sim_model_db.update(model_id, updated_model)

@router.delete("/sim/models/{model_id}")
def delete_sim_model(model_id: str):
    if not sim_model_db.get(model_id):
        raise HTTPException(status_code=404, detail="Model not found")
    sim_model_db.delete(model_id)
    return {"status": "deleted"}

@router.get("/sim/models", response_model=List[SimModel])
def list_sim_models():
    return sim_model_db.list_all()

@router.get("/sim/models/summary", response_model=List[dict])
def list_sim_model_summaries():
    return sim_model_db.list_summaries()
