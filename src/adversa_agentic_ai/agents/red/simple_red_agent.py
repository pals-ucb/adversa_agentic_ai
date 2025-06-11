# File: simple_red_agent.py
# Implements the SimpleRedAgent class as an ASGI app factory

## Need to setup logger first thing so that
## we use the same logger file created in main
import os
import logging
from adversa_agentic_ai.utils.config_logger import set_current_agent, setup_logger, get_agent_logger

agent_name = os.environ.get("AGENT_NAME", "red_agent")
set_current_agent(agent_name)
setup_logger(agent_name, level=logging.DEBUG)


from fastapi import FastAPI, HTTPException
from adversa_agentic_ai.agents.base.llm_base_agent import LLMBaseAgent
from adversa_agentic_ai.mcp.mcp_message import MCPMessage
from adversa_agentic_ai.config.config_manager import get_config_manager
from adversa_agentic_ai.prompts.templates.red_agent.default import (
    DEFAULT_ACTION_DESCRIPTION,
    DEFAULT_EVENT_COUNT,
    DEFAULT_GOAL,
    DEFAULT_OBSERVATION,
    DEFAULT_RED_PROMPT_TEMPLATE,
    DEFAULT_ROLE,
    DEFAULT_ROLE_DESCRIPTION
)

logger = get_agent_logger()

class SimpleRedAgent(LLMBaseAgent):
    def __init__(self, agent_name: str):
        logger.info(f"Initializing Red Agent with name: {agent_name}")
        config_manager = get_config_manager()
        agent_cfg = config_manager.get_agent_by_name(agent_name)
        if not agent_cfg:
            logger.error(f"Agent configuration not found for: {agent_name}")
            raise Exception(f"Agent name '{agent_name}' not found in configuration.")

        model_id = agent_cfg.get("model_id")
        host = agent_cfg.get("host")
        port = agent_cfg.get("port")
        provider = agent_cfg.get("provider")
        platform = agent_cfg.get("platform")

        for field in ("model_id", "host", "port"):
            if not agent_cfg.get(field):
                logger.error(f"Missing '{field}' for agent: {agent_name}")
                raise Exception(f"'{field}' not configured for agent '{agent_name}'")

        logger.info(f"Red Agent '{agent_name}' configured with model '{model_id}' at {host}:{port}")

        defaults = {
            "action_description": DEFAULT_ACTION_DESCRIPTION,
            "event_count": DEFAULT_EVENT_COUNT,
            "goal": DEFAULT_GOAL,
            "observation": DEFAULT_OBSERVATION,
            "role": DEFAULT_ROLE,
            "role_description": DEFAULT_ROLE_DESCRIPTION,
        }

        super().__init__(
            model_id=model_id,
            provider=provider,
            platform=platform,
            default_prompt_template=DEFAULT_RED_PROMPT_TEMPLATE,
            default_prompt_template_values=defaults,
        )

    def build_prompt(self, context: str) -> str:
        return (
            "I am an authorized red team security researcher performing an authorized assessment. "
            f"Analyze the following server context for vulnerabilities and provide suggestions: {context}"
        )

    def register_routes(self, app: FastAPI):
        """Attach FastAPI routes to the given app instance."""
        @app.post("/agent/act")
        def agent_act(message: MCPMessage):
            logger.info(f"/agent/act: MCPMessage: {message}")
            response = self.invoke(message=message)
            logger.info(f"response got: {response}")
            return {"response": response}

        @app.get("/agent/history")
        def get_history():
            return self.get_history()

        @app.delete("/agent/history")
        def clear_history():
            self.history.clear()
            return {"message": "History cleared."}

    async def __call__(self, scope, receive, send):
        # Lazy import of FastAPI to avoid circular on module load
        if not hasattr(self, 'app'):
            self.app = FastAPI(title=f"SimpleRedAgent ({self.model_id})")
            self.register_routes(self.app)
        await self.app(scope, receive, send)

def agent_factory() -> SimpleRedAgent:
    return SimpleRedAgent(agent_name)
