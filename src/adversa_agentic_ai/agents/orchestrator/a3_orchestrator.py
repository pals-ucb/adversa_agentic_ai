import os
import logging
import re
import uuid
import boto3
import json
import requests
from datetime import datetime, timezone
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import Dict
from adversa_agentic_ai.utils.config_logger import setup_logger, set_current_agent, get_agent_logger
# Initialize logging early
agent_name = os.getenv("AGENT_NAME", "orchestrator_agent")
set_current_agent(agent_name)
setup_logger(agent_name, level=logging.DEBUG)
logger = get_agent_logger()

from adversa_agentic_ai.config.config_manager import get_config_manager
from adversa_agentic_ai.agents.base.llm_base_agent import LLMBaseAgent
from adversa_agentic_ai.api.schemas.sim_models import SimModel
from adversa_agentic_ai.api.schemas.sim import (
    SimRequest, 
    SimResponse, 
    SimStatus,
    AgentLLMResponse,
    SimStepResult,
    SimStepResponse
)
from adversa_agentic_ai.api.schemas.internal.orchestrator_schemas import (
    LoadModelRequest,
    LoadModelResponse
)
from adversa_agentic_ai.agents.orchestrator.a3_sim_model_context import AgentContext, SimModelContext

class OrchestratorAgent(LLMBaseAgent):
    def __init__(self, agent_name: str):
        logger.info(f"Initializing Orchestrator Agent: {agent_name}")
        cfg = get_config_manager().get_agent_by_name(agent_name)
        if not cfg:
            raise Exception(f"Agent config not found: {agent_name}")
        for k in ("model_id", "provider", "platform"):
            if not cfg.get(k):
                raise Exception(f"'{k}' missing in config")
        self.managed_agents = cfg.get("managed_agents", [])
        super().__init__(
            model_id=cfg["model_id"],
            provider=cfg["provider"],
            platform=cfg["platform"],
            max_tokens=cfg.get("max_tokens", 512)
        )
        logger.info("Orchestrator model configured")
        self.models_store: Dict[str, dict] = {}

    def _find_sim_context(self, model_id: str) -> SimModelContext:
        for sim_id, sim_context in self.models_store.items():
            if sim_context.model_id == model_id:
                return sim_context
        return None

    def register_routes(self, app: FastAPI):
        @app.post(
            "/aaa/agents/orchestrator/sim/model/load", 
            response_model=LoadModelResponse,
            status_code=201
        )
        def load_model(req: LoadModelRequest):
            model_id = req.model_id
            logger.info(f"Loading model '{model_id}' from S3: bucket={req.s3_bucket}, key={req.s3_path}")
            sim_context = self._find_sim_context(model_id)
            if sim_context:
                sim_id = sim_context.sim_id
            else:
                sim_id = str(uuid.uuid4())
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
                a3_model = SimModel.model_validate(json_model)  # Pydantic v2
            except ValidationError as e:
                logger.error(f"SimModel validation failed: {e}")
                raise HTTPException(status_code=422, detail="Invalid SimModel format") from e

            context = SimModelContext(model_id=req.model_id, a3_model = a3_model)
            if not context.init_cbsim_model():
                raise HTTPException(status_code=500, detail="Model conversion error") 
            # Store in-memory
            context.sim_id = sim_id
            context.status = SimStatus.Loaded
            self.models_store[sim_id] = context
            logger.info(f"Adversa Model: {model_id} ready to run, sim_id: {sim_id}")
            rsp = LoadModelResponse(sim_id=sim_id, model_id=req.model_id, sim_status=SimStatus.Loaded)
            return rsp

        @app.get("/aaa/agents/orchestrator/sim/model/{model_id}")
        def get_model(model_id: str):
            logger.info(f"Get model details: {model_id}")
            sim_model = self.models_store.get(model_id)
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

        @app.post(
            "/aaa/agents/orchestrator/sim/model/run",
            response_model=SimResponse,
            status_code=201
        )
        def run_simulation(req: SimRequest):
            req_ts = datetime.now(timezone.utc)
            logger.info(f"Simulation run request: sim_id={req.sim_id}, mode={req.step_mode}")
            
            if req.sim_id not in self.models_store:
                logger.error(f"Simulation context not found: {req.sim_id}")
                raise HTTPException(status_code=404, detail=f"Sim id {req.sim_id} not found, Model not loaded!")
            try:
                sim_context: SimModelContext = self.models_store.get(req.sim_id)
                if sim_context.status not in {"Loaded", "Paused", "Running"}:
                    logger.error(f"Sim ID {req.sim_id} is in invalid state: {sim_context.status}")
                    raise HTTPException(status_code=400, detail=f"Model not in runnable state, current state: {sim_context.status}")
                sim_context.set_current_step_node_id()
                node_obs = sim_context.get_current_observations()
                node_reward = sim_context.get_current_reward() 
                logger.debug(f"Step {sim_context.step} obs: {node_obs}, reward: {node_reward}")
                step_results = []
                logger.debug(f"Taking step actions with managed agents: {self.managed_agents}")
                for agent_cfg in self.managed_agents:
                    agent_id = agent_cfg["id"]
                    role = agent_cfg["role"]
                    agent_url = agent_cfg["url"]
                    if agent_id == "red":
                        mcp_msg = sim_context.build_red_agent_MCPMessage()
                    elif agent_id == "blue":
                        mcp_msg = sim_context.build_blue_agent_MCPMessage()
                    else:
                        logger.error(f"Unsupported agent type: {agent_id}")
                        continue
                    try:
                        logger.info(f"Sending MCPMessage to {agent_id} at {agent_url}/aaa/agent/action")
                        resp = requests.post(f"{agent_url}/aaa/agent/action", json=mcp_msg.model_dump(mode="json"))
                        resp.raise_for_status()
                        result_json = resp.json()
                        logger.debug(f"Response from {agent_id}: {result_json}")
                        llm_responses = []
                        reward = 0.0
                        for entry in result_json.get("response", []):
                            llm_resp = AgentLLMResponse(
                                suggested_action=entry.get("suggested_action"),
                                best_action=entry.get("best_action"),
                                rationale=entry.get("rationale"),
                                confidence=entry.get("confidence", 0.0),
                                commentary=entry.get("commentary")
                            )
                            llm_responses.append(llm_resp)
                            if entry.get("confidence", 0.0)*node_reward > reward:
                                reward = entry.get("confidence", 0.0)*node_reward 

                        step_result = SimStepResult(
                            agent_id=agent_id,
                            epoch=sim_context.epoch,
                            step=sim_context.step,
                            observation=mcp_msg.observation,
                            result=llm_responses,
                            reward=reward,
                            timestamp=datetime.utcnow()
                        )
                        agent_context = sim_context.agent_context.setdefault(agent_id, AgentContext(agent_id=agent_id, history=[], total_reward=0))
                        # Store to sim_context history
                        agent_context.history.append(step_result.model_dump(mode="json"))
                        agent_context.total_reward += reward
                        step_results.append(step_result)

                    except Exception as e:
                        logger.error(f"Error communicating with agent {agent_id}: {e}")
                        error_result = SimStepResult(
                            agent_id=agent_id,
                            epoch=sim_context.epoch,
                            step=sim_context.step,
                            observation=mcp_msg.observation,
                            result=[],
                            reward=0.0,
                            timestamp=datetime.utcnow()
                        )
                        step_results.append(error_result)

                # Advance sim state
                sim_context.status = SimStatus.Running
                logger.info(f"Step {sim_context.step} completed.")
                sim_context.advance_step()

                # Construct response
                sim_step_response = SimStepResponse(
                    sim_status=sim_context.status,
                    step_results=step_results
                )

                return SimResponse(
                    sim_id=req.sim_id,
                    sim_status=sim_context.status,
                    sim_result=[sim_step_response],
                    req_ts=req_ts,
                    rsp_ts=datetime.now(timezone.utc)
                )

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
