import logging
import uvicorn
from config.config_manager import config_manager
from utils.config_logger import setup_logger

# Load app name from config or default to 'red_agent'
app_name = config_manager.get("agent", "name", default="red_agent")

# Set up structured logging
setup_logger(app_name)
logger = logging.getLogger(app_name)

def launch_uvicorn():
    host = config_manager.get("agent", "host", default="0.0.0.0")
    port = config_manager.get("agent", "port", default=8000)
    log_level = config_manager.get("agent", "uvicorn_log_level", default="warning")

    logger.info(f"Starting Red Agent: {app_name} on {host}:{port}")
    
    uvicorn.run(
        "simple_red_agent:app",  
        host=host,
        port=port,
        reload=True,
        log_level=log_level,
        access_log=False
    )

if __name__ == "__main__":
    launch_uvicorn()
