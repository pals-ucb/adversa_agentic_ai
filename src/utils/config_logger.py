import os
import logging
from utils.fsutils import find_workspace_root

def setup_logger(app_name: str) -> logging.Logger:
    workspace_root = find_workspace_root()
    log_dir = os.path.join(workspace_root, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, f"{app_name}.log")

    log_format = "[%(asctime)s] %(levelname)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path)
        ]
    )

    return logging.getLogger(app_name)
# logger_config.py