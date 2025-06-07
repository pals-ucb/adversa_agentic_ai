# File: src/api/api_server.py
from adversa_agentic_ai.utils.config_logger import (
    set_current_agent,
    setup_logger,
    get_agent_logger
)

app_name='API-Server'
set_current_agent(app_name)
setup_logger(app_name)
logger = get_agent_logger()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import time

# Routers
from .routers.agents import router as agents_router
from .routers.providers import router as providers_router
from .routers.prompt_templates import router as prompt_templates_router
from .routers.sim_models import router as sim_models_router
from .routers.sim import router as sim_runtime_router
from .config_api import router as config_router

app = FastAPI(
    title="Simulation API Server",
    version="1.0.0",
    description="API Server for Managing Agents, Sim Models, Prompts, Providers, and Simulations"
)

# Allow frontend CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"--> {request.method} {request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    logger.info(f"<-- {request.method} {request.url.path} {response.status_code} [{process_time:.2f}ms]")

    return response


# === Register All Routers with Prefixes ===

app.include_router(sim_models_router, prefix="/aaa", tags=["sim/models"])
app.include_router(sim_runtime_router, prefix="/aaa", tags=["sim"])

app.include_router(agents_router, prefix="/aaa", tags=["agents"])
app.include_router(providers_router, prefix="/aaa", tags=["providers"])

app.include_router(prompt_templates_router, prefix="/aaa", tags=["prompt/templates"])
# app.include_router(prompt_instances_router, prefix="/aaa", tags=["prompt/instances"])  # future

# include config router
app.include_router(config_router, prefix="/aaa", tags=["config"])

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


