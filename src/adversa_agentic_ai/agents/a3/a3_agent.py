# File: a3_agent.py
# Implements the SimpleRedAgent class as an ASGI app factory

## Need to setup logger first thing so that
## we use the same logger file created in main
import os
import re
import logging
from enum import Enum
from adversa_agentic_ai.utils.config_logger import set_current_agent, setup_logger, get_agent_logger

agent_name = os.environ.get("AGENT_NAME", "red_agent")
set_current_agent(agent_name)
setup_logger(agent_name, level=logging.DEBUG)

import json
from fastapi import FastAPI, HTTPException
from typing import List
from adversa_agentic_ai.agents.base.llm_base_agent import LLMBaseAgent
from adversa_agentic_ai.mcp.mcp_message import MCPMessage
from adversa_agentic_ai.config.config_manager import get_config_manager
from adversa_agentic_ai.schemas.llm import parse_and_validate_llm_response

logger = get_agent_logger()

class A3Agent(LLMBaseAgent):
    def __init__(self, agent_name: str):
        logger.info(f"Initializing A3 Agent with name: {agent_name}")
        config_manager = get_config_manager()
        agent_cfg = config_manager.get_agent_by_name(agent_name)
        if not agent_cfg:
            logger.error(f"Agent configuration not found for: {agent_name}")
            raise Exception(f"Agent name '{agent_name}' not found in configuration.")

        model_id = agent_cfg.get("model_id")
        provider = agent_cfg.get("provider")
        platform = agent_cfg.get("platform")
        max_tokens = agent_cfg.get("max_token", 512)
        for field in ("model_id", "provider", "platform"):
            if not agent_cfg.get(field):
                logger.error(f"Missing '{field}' for agent: {agent_name}")
                raise Exception(f"'{field}' not configured for agent '{agent_name}'")

        logger.info(f"A3 Agent '{agent_name}' configured with model '{model_id}' provider: {provider} platform: {platform}")
        super().__init__(
            model_id=model_id,
            provider=provider,
            platform=platform,
            max_tokens=max_tokens
        )

    '''def build_prompt(self, context: str) -> str:
        return (
            "I am an authorized red team security researcher performing an authorized assessment. "
            f"Analyze the following server context for vulnerabilities and provide suggestions: {context}"
        )'''

    def register_routes(self, app: FastAPI):
        """Attach FastAPI routes to the given app instance."""
        @app.post("/aaa/agent/action")
        def agent_action(message: MCPMessage):
            logger.info(f"/aaa/agent/action: MCPMessage: {message}")
            response = self.invoke(message=message)
            llm_actions = parse_and_validate_llm_response(response) 
            logger.info(f"response got: {llm_actions}")
            return {"response": llm_actions}

        @app.get("/aaa/agent/history")
        def get_history():
            return self.get_history()

        @app.delete("/aaa/agent/history")
        def clear_history():
            self.history.clear()
            return {"message": "History cleared."}

    async def __call__(self, scope, receive, send):
        # Lazy import of FastAPI to avoid circular on module load
        if not hasattr(self, 'app'):
            self.app = FastAPI(title=f"SimpleRedAgent ({self.model_id})")
            self.register_routes(self.app)
        await self.app(scope, receive, send)

def agent_factory() -> A3Agent:
    return A3Agent(agent_name)
