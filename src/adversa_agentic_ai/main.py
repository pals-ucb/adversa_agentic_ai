from mangum import Mangum
from adversa_agentic_ai.api.api_server import app

handler = Mangum(app, api_gateway_base_path="/Prod")  # AWS Lambda entrypoint

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("adversa_agentic_ai.api.api_server:app", host="0.0.0.0", port=8080, reload=True)
