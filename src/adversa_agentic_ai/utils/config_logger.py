import os
import logging
from adversa_agentic_ai.utils.fsutils import find_workspace_root

# Global agent name to make logging clealy separated across
# agents
_agent_name = None

def set_current_agent(name: str):
    global _agent_name
    _agent_name = name
    print(f"Setting agent name: {_agent_name}")

def setup_logger(app_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create (or get) a logger named `app_name`, attach console+file handlers,
    and set both the logger and its handlers to `level` or above.
    """
    # 1) get or create the logger
    print(f"Setting up logger name: Global {_agent_name} passed: {app_name}")
    logger = logging.getLogger(app_name)
    logger.setLevel(level)
    logger.propagate = False   # avoid double‐logging if root also has handlers

    # 2) if we've already added handlers, don’t add again
    if logger.handlers:
        return logger

    # 3) choose format
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        log_fmt = "[%(levelname)s] %(message)s"
    else:
        log_fmt = "[%(asctime)s] %(levelname)s: %(message)s"

    formatter = logging.Formatter(log_fmt)

    # 4) console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # 5) file handler (local only)
    if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        root = "/tmp"
        os.makedirs(os.path.join(root, "logs"), exist_ok=True)
        fh = logging.FileHandler(os.path.join(root, "logs", f"{app_name}.log"))
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def get_agent_logger():
    import traceback
    print(f"Using agent name : {_agent_name}")
    if not _agent_name:
        traceback.print_stack() 
    return logging.getLogger(_agent_name if _agent_name else "default")
