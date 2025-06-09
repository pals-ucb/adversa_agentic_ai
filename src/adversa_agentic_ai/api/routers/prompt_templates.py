from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from typing import List
from ..schemas.prompt_templates import PromptTemplate
from ..stores.prompt_template_store import PromptTemplateStore

router = APIRouter(
    prefix="/prompt",
    tags=["Prompt Templates"],
    responses={404: {"description": "Template not found"}}
)

prompt_store = PromptTemplateStore()

@router.post(
    "/templates",
    response_model=PromptTemplate,
    summary="Create a new prompt template",
    description="Registers a new prompt template with optional placeholders and default values."
)
def create_template(template: PromptTemplate, background_tasks: BackgroundTasks):
    if prompt_store.get(template.id):
        raise HTTPException(status_code=400, detail="Template already exists")
    return prompt_store.save(template, background_tasks)

@router.get(
    "/templates/{template_id}",
    response_model=PromptTemplate,
    summary="Get a prompt template",
    description="Retrieves a prompt template by its unique ID."
)
def get_template(template_id: str):
    template = prompt_store.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put(
    "/templates/{template_id}",
    response_model=PromptTemplate,
    summary="Update a prompt template",
    description="Updates the specified prompt template with new values and placeholder configuration."
)
def update_template(template_id: str, updated: PromptTemplate, background_tasks: BackgroundTasks):
    if not prompt_store.get(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return prompt_store.update(template_id, updated, background_tasks)

@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a prompt template",
    description="Deletes the specified prompt template from the system."
)
def delete_template(template_id: str, background_tasks: BackgroundTasks):
    if not prompt_store.get(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    prompt_store.delete(template_id, background_tasks)
    return {"status": "deleted"}

@router.get(
    "/templates",
    response_model=List[PromptTemplate],
    summary="List all prompt templates",
    description="Returns a list of all saved prompt templates, including placeholder metadata."
)
def list_templates(background_tasks: BackgroundTasks):
    return prompt_store.list_all(background_tasks)
