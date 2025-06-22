# File: src/adversa_agentic_ai/api/schemas/internal/orchestrator_schemas.py
from pydantic import BaseModel, Field
from typing import Literal, Optional 
from enum import Enum
from adversa_agentic_ai.api.schemas.sim import SimStatus


class LoadModelRequest(BaseModel):
    s3_bucket: str
    s3_path: str
    model_id: str

class LoadModelResponse(BaseModel):
    sim_id: str = Field(..., description="Unique ID for the simulation instance")
    model_id: str = Field(..., description="The model ID used to create the simulation")
    sim_status: SimStatus = Field(..., description="Status of the simulation loading")
    message: Optional[str] = Field(None, description="Model load failure/error status message")
