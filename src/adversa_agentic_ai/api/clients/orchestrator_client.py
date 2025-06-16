# File: src/adversa_agentic_ai/api/clients/orchestration_client.py

import os
import requests
import logging
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
            response = requests.post(url, json=request.model_dump())
            response.raise_for_status()
            return LoadModelResponse(**response.json())
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to call orchestrator load_model: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
