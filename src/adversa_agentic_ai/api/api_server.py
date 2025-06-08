# File: src/api/api_server.py
import os
from adversa_agentic_ai.utils.config_logger import (
    set_current_agent,
    setup_logger,
    get_agent_logger
)

app_name='API-Server'
set_current_agent(app_name)
setup_logger(app_name)
logger = get_agent_logger()

from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import time

# Routers
from .routers.agents import router as agents_router
from .routers.providers import router as providers_router
from .routers.prompt_templates import router as prompt_templates_router
from .routers.sim_models import router as sim_models_router
from .routers.sim import router as sim_runtime_router
from .config_api import router as config_router

stage = os.getenv("STAGE", "Prod")           # or hard-code "Prod"
app = FastAPI(
    title="Adversarial Agentic AI API",
    root_path=f"/{stage}",                    # ← this makes spec-url include /Prod
    openapi_url="/openapi.json",              # still the same path, but prefixed
    docs_url="/docs",
    redoc_url="/redoc",
    version="0.1.0",
    description="""
API for managing simulation models (`SimModel`), PromptTemplates, Agents(Red/Blue), Providers and LLM Selections.
The API also allows running Simulations using the /aaa/sim APIs.
This service powers adversarial agentic AI workflows using FastAPI and AWS Lambda.
The current API schema fully support SimModel creation, listing, get, updates and deletes persistently.
This is enabled for SimModels and PromptTemplates.
""",
    contact={
        "name": "Pals Chinnakannan",
        "email": "palsc@berkeley.edu"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
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

landing_page_html = '''
<!DOCTYPE html>
<html>
<head>
  <title>Adversa Agentic AI API</title>
</head>
<body>
  <h1>Adversa Agentic AI API</h1>
  <p>Welcome to the Adversarial Agentic AI API. This is a FastAPI-based service deployed via AWS SAM, providing a RESTful interface to the Adversarial Agentic AI system. Use this landing page to learn how to explore and use the API.</p>

  <h2>Key General Endpoints</h2>
  <ul>
    <li><code>/docs</code> – Interactive API documentation (Swagger UI) for testing and exploring endpoints:contentReference[oaicite:0]{index=0}.</li>
    <li><code>/redoc</code> – Alternative API documentation (ReDoc) with a different interface for viewing endpoints and schemas:contentReference[oaicite:1]{index=1}.</li>
    <li><code>/openapi.json</code> – The OpenAPI schema (JSON format). This specification can be used by tools or for generating client SDKs:contentReference[oaicite:2]{index=2}.</li>
  </ul>

  <h2>Generating Client SDKs</h2>
  <p>You can generate client libraries using the API’s OpenAPI specification. For example, using the <em>OpenAPI Generator CLI</em> tool:contentReference[oaicite:3]{index=3}:</p>
  <ul>
    <li><strong>Python SDK:</strong> Run <code>openapi-generator-cli generate -g python -i https://&lt;api-id&gt;.execute-api.&lt;region&gt;.amazonaws.com/Prod/openapi.json -o ./client/python</code> to generate a Python client library:contentReference[oaicite:4]{index=4}.</li>
    <li><strong>JavaScript SDK:</strong> Run <code>openapi-generator-cli generate -g javascript -i https://&lt;api-id&gt;.execute-api.&lt;region&gt;.amazonaws.com/Prod/openapi.json -o ./client/js</code> to generate a JavaScript client.</li>
  </ul>

  <h2>Authentication</h2>
  <p><strong>None required:</strong> All endpoints are public and can be accessed without any API key or token.</p>
</body>
</html>

'''

@app.get("/", include_in_schema=False)
def root():
    # Return the landing page HTML as a response
    return HTMLResponse(content=landing_page_html, status_code=200)

@app.get("/_debug_root")
def debug_root(request: Request):
    return {
        "root_path": request.scope.get("root_path"),
        "path": request.url.path
    }


