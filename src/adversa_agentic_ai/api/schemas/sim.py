from re import L
from pandas import Timestamp
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Any
from enum import Enum
from datetime import datetime

class SimStatus(str, Enum):
    Loaded = "Loaded"
    LoadFailed = "LoadFailed"
    Running = "Running"
    RunFailed = "RunFailed"
    StepFailed = "StepFailed"
    Paused = "Paused"
    Finished = "Finished"
    Unloaded = "Unloaded"

class SimModelLoadRequest(BaseModel):
    model_id: str = Field(..., description="The adversa model ID returned when a model is created")

class SimModelLoadResponse(BaseModel):
    sim_id: str = Field(..., description="Simulation ID that is used for subsequent sim operations")
    sim_status: SimStatus = Field(..., description="Initial status of the sim after loading the model ")
    message: Optional[str] = Field(None, description="Optional error or status message for additional context")

class Observation(BaseModel):
    id: str = Field(..., description="Node ID")
    name: str = Field(..., description="Node Name")
    node_type: str = Field(..., description="Node Type (e.g., Asset, Person)")
    properties: Dict[str, Any] = Field(..., description="Key-value pairs of properties")
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="List of vulnerability objects")
    reachable_nodes: List[str] = Field(default_factory=list, description="List of reachable node IDs")
    credentials: List[str] = Field(default_factory=list, description="List of credential IDs")

class AgentLLMResponse(BaseModel):
    suggested_action: str = Field(..., description="Action proposed by the agent")
    best_action: Optional[str] = Field(None, description="Best action as selected by the agent")
    rationale: str = Field(..., description="Reasoning behind the chosen action")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    commentary: Optional[str] = Field(None, description="Optional narrative explanation")

class SimStepResult(BaseModel):
    agent_id: str = Field(..., description="Which agent took the action")
    epoch: int = Field(..., description="Epoch during which this step occurred")
    step: int = Field(..., description="Step number in the epoch")
    observation: Optional[Observation] = Field(
        None, description="What the agent observed at the step")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the step result was recorded")
    result: List[AgentLLMResponse] = Field(..., description="List of LLM-provided actions and rationales")
    reward: Optional[float] = Field(None, description="Reward achieved based on result and node reward weight")

class SimStepResponse(BaseModel):
    sim_status: str = Field(..., description="Final sim status after the step")
    step_results: List[SimStepResult] = Field(..., description="All agent results for this step")

class SimRequest(BaseModel):
    sim_id: str = Field(..., description="ID of the Sim to run, i.e.,the sim_id returned by LoadModel")
    step_mode: bool = Field(False, description="Whether to run in step-by-step mode (`True`) or full run (`False`)")
    timestamp: Optional[datetime] = Field(..., description="Optional datetime during the request creatin.)") 

class SimResponse(BaseModel):
    sim_id: str = Field(..., description="Simulation ID")
    sim_status: SimStatus = Field(..., description="Current status of the sim after the step")
    sim_result: List[SimStepResponse] = Field(..., description="The result message returned by the simulatin step")
    req_ts: datetime = Field(..., description="Optional datetime during the request creatin.)")
    rsp_ts: datetime = Field(..., description="Optional datetime during the request creatin.)")

class SimStepDetail(BaseModel):
    step: int = Field(..., description="Sequential step number")
    observation: Dict[str, Any] = Field(..., description="Observed environment state at this step")
    prompts: Dict[str, str] = Field(..., description="Prompt(s) issued by the agent during this step")
    tools_used: Optional[Dict[str, Any]] = Field(None, description="Any tools used by the agent at this step")
    actions: Dict[str, Any] = Field(..., description="Actions taken by the agent")
    step_output: Dict[str, Any] = Field(..., description="Output or result of this step")

class SimState(BaseModel):
    sim_id: str = Field(..., description="Unique simulation ID")
    current_step: int = Field(..., description="Index of the current simulation step")
    sim_status: SimStatus = Field(..., description="Overall status of the simulation")
    steps: Dict[int, SimStepDetail] = Field(..., description="Mapping of step numbers to detailed step execution records")
