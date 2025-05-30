# api/config_api.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.config_manager import config_manager

router = APIRouter()

class ConfigUpdateRequest(BaseModel):
    value: str | int | float | bool | dict | list

@router.get("/config/{section:path}")
def get_config_section(section: str):
    keys = section.split("/")
    value = config_manager.get(*keys)
    if value is None:
        raise HTTPException(status_code=404, detail="Config section not found")
    return {"key": section, "value": value}

@router.put("/config/{section:path}")
def update_config_section(section: str, req: ConfigUpdateRequest):
    try:
        config_manager.update(section, req.value)
        return {"message": f"Updated {section} successfully", "value": req.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {e}")

@router.get("/config")
def get_full_config():
    return config_manager.all()


'''
# Code for mounting the above router from the main 
# service for supporting all the api include config
# UX will call the update

from fastapi import FastAPI
from api.config_api import router as config_api

app = FastAPI()
app.include_router(config_api, prefix="/api")


'''

'''
# A CURL example to show how to invoke the config api
curl -X PUT http://localhost:8000/api/config/aws/bedrock/region \
  -H "Content-Type: application/json" \
  -d '{"value": "us-west-2"}'

'''