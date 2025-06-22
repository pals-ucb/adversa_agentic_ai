# File: src/adversa_agentic_ai/api/clients/orchestration_client.py

import os
import requests
import logging
from adversa_agentic_ai.api.schemas.sim import SimRequest, SimResponse, SimStatus
from adversa_agentic_ai.api.schemas.internal.orchestrator_schemas import LoadModelRequest, LoadModelResponse
from adversa_agentic_ai.utils.config_logger import get_agent_logger

logger = get_agent_logger()

class OrchestrationClient:
    """
    HTTP client to communicate with the OrchestratorAgent.
    Loads configuration from environment.
    """

    def __init__(self):
        self.endpoint = os.environ.get("A3_ORCHESTRATOR_ENDPOINT", None)
        if not self.endpoint:
            raise RuntimeError("Missing required environment variable: A3_ORCHESTRATOR_ENDPOINT")
        self.endpoint = self.endpoint.rstrip("/")

    def load_model(self, request: LoadModelRequest) -> LoadModelResponse:
        """
        Call the orchestrator to load a simulation model.

        Args:
            request (LoadModelRequest): Model load request payload.

        Returns:
            LoadModelResponse: Response containing simulation ID and status.
        """
        url = f"{self.endpoint}/aaa/agents/orchestrator/sim/model/load"
        logger.info(f"[Orchestrator] POST {url} with model_id={request.model_id}")

        try:
            response = requests.post(url, json=request.model_dump(mode="json"))
            if response.status_code == 404:
                detail = response.json().get("detail", "Model not found")
                logger.warning(f"[404] Orchestrator load model failed for model_id={request.model_id}: {detail}")
                return LoadModelResponse(
                    sim_id=None, 
                    model_id=request.model_id, 
                    sim_status=SimStatus.LoadFailed, 
                    message=detail)
            response.raise_for_status()
            return LoadModelResponse(**response.json())
        except requests.HTTPError as e:
            try:
                error_json = e.response.json()
                detail = error_json.get("detail", e.response.text)
            except Exception:
                detail = e.response.text
            logger.warning(
                f"Orchestrator returned {e.response.status_code} for model_id={request.model_id}: {detail}"
            )
            raise

    def run_sim(self, runSimRequest: SimRequest) -> SimResponse:
        url = f"{self.endpoint}/aaa/agents/orchestrator/sim/model/run"
        logger.info(f"Orchestrator simulation run sim_id={runSimRequest.sim_id}")
        try:
            response = requests.post(url, json=runSimRequest.model_dump(mode="json"))
            if response.status_code == 404:
                detail = response.json().get("detail", "Simulation not found")
                logger.warning(f"[404] Orchestrator run failed for sim_id={runSimRequest.sim_id}: {detail}")
                return SimResponse(
                    sim_id=runSimRequest.sim_id,
                    step=0,
                    epoch=0,
                    sim_status=SimStatus.RunFailed,
                    message=detail  # Optional: add `message: Optional[str]` to schema
                )
            response.raise_for_status()
            return SimResponse(**response.json())
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to orchestrator failed: {str(e)}")
            return SimResponse(
                sim_id=runSimRequest.sim_id,
                step=0,
                epoch=0,
                sim_status=SimStatus.RunFailed,
                message="Connection to orchestrator failed"
            )

