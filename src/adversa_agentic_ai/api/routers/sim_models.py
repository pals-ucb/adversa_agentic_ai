from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from typing import List
from adversa_agentic_ai.utils.config_logger import get_agent_logger
from ..schemas.sim_models import SimModel
from ..stores.sim_model_store import SimModelStore
from botocore.exceptions import ClientError

logger = get_agent_logger()

router = APIRouter(
    prefix="/sim/models",
    tags=["Simulation Models"],
    responses={404: {"description": "SimModel not found"}}
)

sim_model_db = SimModelStore()

@router.post(
    "",
    response_model=SimModel,
    summary="Create a new simulation model",
    description="Creates and stores a new SimModel with associated nodes, vulnerabilities, firewalls, and resources."
)
def create_sim_model(model: SimModel, background_tasks: BackgroundTasks):
    logger.info(f'SimModel: create {model}')
    if sim_model_db.get(model.id):
        raise HTTPException(status_code=400, detail="Model already exists")
    return sim_model_db.save(model, background_tasks)

@router.get(
    "/{model_id}",
    response_model=SimModel,
    summary="Retrieve a simulation model",
    description="Fetches the full SimModel definition using its unique model ID."
)
def get_sim_model(model_id: str):
    model = sim_model_db.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.put(
    "/{model_id}",
    response_model=SimModel,
    summary="Update a simulation model",
    description="Updates an existing SimModel with new configuration, nodes, or properties."
)
def update_sim_model(model_id: str, updated_model: SimModel, background_tasks: BackgroundTasks):
    if not sim_model_db.get(model_id):
        raise HTTPException(status_code=404, detail="Model not found")
    return sim_model_db.update(model_id, updated_model, background_tasks)

@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a simulation model",
    description="Removes a SimModel from the system by its ID."
)
def delete_sim_model(model_id: str, background_tasks: BackgroundTasks):
    if not sim_model_db.get(model_id):
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        sim_model_db.delete(model_id, background_tasks)
        logger.info(f"Sim Model delete completed successfully, model_id: {model_id}")
    except ClientError as ce:
        code = ce.response["Error"]["Code"]
        # 404 for missing key
        if code == "NoSuchKey":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if code in ("AccessDenied", "AllAccessDisabled"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        logger.error(f"Sim Model delete ClientError code: {code}, model_id: {model_id} exception: {ce}")
    except Exception as e:
        # log the unexpected exception
        logger.error(f"Unexpected error deleting S3 object: {e}")
        # return a generic 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error deleting object"
        )
    return




@router.get(
    "",
    response_model=List[SimModel],
    summary="List all simulation models",
    description="Returns a list of all full SimModel records in the system."
)
def list_sim_models(background_tasks: BackgroundTasks):
    return sim_model_db.list_all(background_tasks)

@router.get(
    "/summary",
    response_model=List[dict],
    summary="List simulation model summaries",
    description="Returns a concise summary of each SimModel, including basic metadata."
)
def list_sim_model_summaries(background_tasks: BackgroundTasks):
    return sim_model_db.list_summaries(background_tasks)
