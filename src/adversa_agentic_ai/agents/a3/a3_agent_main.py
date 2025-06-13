import os
import logging
import argparse
import uvicorn
from adversa_agentic_ai.utils.config_logger import setup_logger
from adversa_agentic_ai.utils.config_logger import set_current_agent
#from adversa_agentic_ai.agents.red.simple_red_agent import agent_factory
#from adversa_agentic_ai.config.config_manager import get_config_manager

def parse_args():
    parser = argparse.ArgumentParser(description="Launch A3 Agent")
    parser.add_argument("--agent_name", required=True, help="Name of the agent in the config file.")
    return parser.parse_args()

def launch_uvicorn(args: argparse, config_manager: object, logger: object) -> None:
    os.environ["AGENT_NAME"] = args.agent_name
    agent_cfg = config_manager.get_agent_by_name(args.agent_name)
    if not agent_cfg:
        logger.error(f"Agent configuration not found for: {args.agent_name}")
        raise Exception(f"Agent name '{args.agent_name}' not found in configuration.")
    host = agent_cfg.get("host")
    port = agent_cfg.get("port")
    log_level = config_manager.get("agent", "uvicorn_log_level", default="warning")

    for field in ("model_id", "host", "port"):
        if not agent_cfg.get(field):
           logger.error(f"Missing '{field}' for agent: {args.agent_name}")
           raise Exception(f"'{field}' not configured for agent '{args.agent_name}'")

    logger.info(f"Starting Red Agent: {app_name} on {host}:{port}")
    
    uvicorn.run(
        "adversa_agentic_ai.agents.a3.a3_agent:agent_factory",
        host=host,
        port=port,
        reload=True,
        log_level=log_level,
        access_log=False,
        factory=True
    )

if __name__ == "__main__":
    args = parse_args()
    app_name = args.agent_name
    set_current_agent(app_name)
    setup_logger(app_name)
    logger = logging.getLogger()
    from adversa_agentic_ai.config.config_manager import get_config_manager
    config_manager = get_config_manager()
    launch_uvicorn(args, config_manager, logger)

