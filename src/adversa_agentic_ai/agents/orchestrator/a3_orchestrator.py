import os
import logging
from tkinter.tix import STATUS
import uuid
import boto3
import json
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import Dict, Literal, Optional

from adversa_agentic_ai.utils.config_logger import setup_logger, set_current_agent, get_agent_logger
# Initialize logging early
agent_name = os.getenv("AGENT_NAME", "orchestrator_agent")
set_current_agent(agent_name)
setup_logger(agent_name, level=logging.DEBUG)
logger = get_agent_logger()

from adversa_agentic_ai.config.config_manager import get_config_manager
from adversa_agentic_ai.agents.base.llm_base_agent import LLMBaseAgent
from adversa_agentic_ai.api.schemas.sim_models import SimModel
from adversa_agentic_ai.api.schemas.sim import SimStatus
from adversa_agentic_ai.api.schemas.internal.orchestrator_schemas import (
    LoadModelRequest,
    LoadModelResponse,
    ExecuteRequest,
    ExecuteResponse,
)
from adversa_agentic_ai.models.model_convertor import ConvertedSimModel

class OrchestratorAgent(LLMBaseAgent):
    def __init__(self, agent_name: str):
        logger.info(f"Initializing Orchestrator Agent: {agent_name}")
        cfg = get_config_manager().get_agent_by_name(agent_name)
        if not cfg:
            raise Exception(f"Agent config not found: {agent_name}")
        for k in ("model_id", "provider", "platform"):
            if not cfg.get(k):
                raise Exception(f"'{k}' missing in config")
        super().__init__(
            model_id=cfg["model_id"],
            provider=cfg["provider"],
            platform=cfg["platform"],
            max_tokens=cfg.get("max_tokens", 512)
        )
        logger.info("Orchestrator model configured")
        self.models_store: Dict[str, dict] = {}

    def register_routes(self, app: FastAPI):
        @app.post(
            "/aaa/agents/orchestrator/sim/model/load", 
            response_model=LoadModelResponse,
            status_code=201
        )
        def load_model(req: LoadModelRequest):
            model_id = req.model_id
            logger.info(f"Loading model '{model_id}' from S3: bucket={req.s3_bucket}, key={req.s3_path}")

            # Initialize model_store if not present
            if not hasattr(self, "model_store"):
                self.model_store = {}

            # Download JSON from S3
            s3 = boto3.client("s3")
            try:
                key = f"{req.s3_path}/{req.model_id}.json"
                obj = s3.get_object(Bucket=req.s3_bucket, Key=key)
                raw = obj["Body"].read().decode("utf-8")
            except ClientError as e:
                error_code = e.response["Error"].get("Code", "")
                logger.error(f"S3 get_object failed ({error_code}) for {req.s3_bucket}/{req.s3_path}/{req.model_id}")
                if error_code in ("NoSuchKey", "404"):
                    raise HTTPException(status_code=404, detail="Model file not found in S3")
                else:
                    raise HTTPException(status_code=500, detail="Error accessing S3 bucket") from e

            # Parse JSON
            try:
                json_model = json.loads(raw)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON for '{model_id}': {e}")
                raise HTTPException(status_code=400, detail="Invalid JSON in model") from e

            # Parse JSON into SimModel
            try:
                aaa_model = SimModel.model_validate(json_model)  # Pydantic v2
            except ValidationError as e:
                logger.error(f"SimModel validation failed: {e}")
                raise HTTPException(status_code=422, detail="Invalid SimModel format") from e

            # Convert to CBSim
            try:
                sim_model = ConvertedSimModel(aaa_model)
            except Exception as e:
                logger.exception("Conversion to CBSim failed")
                raise HTTPException(status_code=500, detail="Model conversion error") from e

            # Store in-memory
            sim_id = str(uuid.uuid4())
            self.model_store[sim_id] = {
                "s3_bucket": req.s3_bucket,
                "s3_path": req.s3_path,
                "model_id": req.model_id,
                "model": sim_model,
                "status": SimStatus.Loaded
            }
            logger.info(f"Model '{model_id}' loaded and validated")
            rsp = LoadModelResponse(sim_id=sim_id, model_id=req.model_id, status=SimStatus.Loaded)
            return rsp

        @app.get("/aaa/agents/orchestrator/sim/model/{model_id}")
        def get_model(model_id: str):
            logger.info(f"Get model details: {model_id}")
            sim_model = self.abatchmodels_store.get(model_id)
            if not sim_model:
                raise HTTPException(status_code=404, detail="Model not found")
            return sim_model

        @app.delete("/aaa/agents/orchestrator/sim/model/{model_id}")
        def delete_model(model_id: str):
            logger.info(f"Delete model: {model_id}")
            if model_id in self.models_store:
                del self.models_store[model_id]
                return {"model_id": model_id, "status": "deleted"}
            else:
                raise HTTPException(status_code=404, detail="Model not found")

        @app.post("/aaa/agents/orchestrator/sim/model/{model_id}/executions")
        def execute(model_id: str, req: ExecuteRequest):
            logger.info(f"Execute request: model_id={model_id}, mode={req.mode}")
            if model_id not in self.models_store:
                raise HTTPException(status_code=404, detail="Model not loaded")
            try:
                if req.mode == "step":
                    if req.input is None:
                        raise HTTPException(status_code=400, detail="Missing 'input' for step")
                    out = self.invoke_step(model_id, req.input)
                else:
                    out = self.invoke_full_run(model_id)
                return {"model_id": model_id, "mode": req.mode, "result": out}
            except Exception as e:
                logger.exception("Execution error")
                raise HTTPException(status_code=500, detail=str(e))

    async def __call__(self, scope, receive, send):
        if not hasattr(self, "app"):
            self.app = FastAPI(title=f"Orchestrator ({self.model_id})")
            self.register_routes(self.app)
        await self.app(scope, receive, send)

def orchestrator_factory() -> OrchestratorAgent:
    return OrchestratorAgent(agent_name)
