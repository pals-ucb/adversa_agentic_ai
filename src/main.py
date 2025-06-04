# File: src/main.py
# API Server main entry point

import uvicorn
from api.api_server import app

if __name__ == "__main__":
    uvicorn.run("api.api_server:app", host="0.0.0.0", port=8080, reload=True)
