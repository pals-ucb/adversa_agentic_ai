from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class SimStatus(str, Enum):
    NOT_STARTED = "not_started"   # Simulation created but not yet run
    RUNNING = "running"           # Simulation is currently in progress
    COMPLETED = "completed"       # Simulation has completed successfully
    ERROR = "error"               # Simulation terminated due to an error

class SimRequest(BaseModel):
    sim_model_id: str = Field(..., description="ID of the SimModel to run")
    step_mode: bool = Field(False, description="Whether to run in step-by-step mode (`True`) or full run (`False`)")

class SimResponse(BaseModel):
    sim_id: str = Field(..., description="Unique ID assigned to the simulation instance")
    status: SimStatus = Field(..., description="Current status of the simulation")

class SimStepRequest(BaseModel):
    sim_id: str = Field(..., description="Simulation ID to execute the next step")

class SimStepResponse(BaseModel):
    sim_id: str = Field(..., description="Simulation ID")
    step_number: int = Field(..., description="Step number just executed")
    state: Dict[str, Any] = Field(..., description="Current state snapshot after the step")

class SimStepDetail(BaseModel):
    step_number: int = Field(..., description="Sequential step number")
    observation: Dict[str, Any] = Field(..., description="Observed environment state at this step")
    prompts: Dict[str, str] = Field(..., description="Prompt(s) issued by the agent during this step")
    tools_used: Optional[Dict[str, Any]] = Field(None, description="Any tools used by the agent at this step")
    actions: Dict[str, Any] = Field(..., description="Actions taken by the agent")
    step_output: Dict[str, Any] = Field(..., description="Output or result of this step")

class SimState(BaseModel):
    sim_id: str = Field(..., description="Unique simulation ID")
    current_step: int = Field(..., description="Index of the current simulation step")
    status: SimStatus = Field(..., description="Overall status of the simulation")
    steps: Dict[int, SimStepDetail] = Field(..., description="Mapping of step numbers to detailed step execution records")
