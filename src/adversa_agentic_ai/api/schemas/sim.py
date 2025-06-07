# Updated schemas/sim.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class SimStatus(str, Enum):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

class SimRequest(BaseModel):
    sim_model_id: str
    step_mode: bool = False  # True for step-by-step, False for full run

class SimResponse(BaseModel):
    sim_id: str
    status: SimStatus

class SimStepRequest(BaseModel):
    sim_id: str

class SimStepResponse(BaseModel):
    sim_id: str
    step_number: int
    state: Dict[str, Any]

class SimStepDetail(BaseModel):
    step_number: int
    observation: Dict[str, Any]
    prompts: Dict[str, str]
    tools_used: Optional[Dict[str, Any]] = None
    actions: Dict[str, Any]
    step_output: Dict[str, Any]

class SimState(BaseModel):
    sim_id: str
    current_step: int
    status: SimStatus
    steps: Dict[int, SimStepDetail]

