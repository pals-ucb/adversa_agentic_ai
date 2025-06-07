# File: src/api/routers/prompt_templates.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from ..schemas.prompt_templates import PromptTemplate
from ..stores.prompt_template_store import PromptTemplateStore

router = APIRouter(prefix="/prompt", tags=["prompt"])

prompt_store = PromptTemplateStore()

@router.post("/templates", response_model=PromptTemplate)
def create_template(template: PromptTemplate, background_tasks: BackgroundTasks):
    if prompt_store.get(template.id):
        raise HTTPException(status_code=400, detail="Template already exists")
    return prompt_store.save(template, background_tasks)

@router.get("/templates/{template_id}", response_model=PromptTemplate)
def get_template(template_id: str):
    template = prompt_store.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates/{template_id}", response_model=PromptTemplate)
def update_template(template_id: str, updated: PromptTemplate, background_tasks: BackgroundTasks):
    if not prompt_store.get(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return prompt_store.update(template_id, updated, background_tasks)

@router.delete("/templates/{template_id}")
def delete_template(template_id: str, background_tasks: BackgroundTasks):
    if not prompt_store.get(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    prompt_store.delete(template_id, background_tasks)
    return {"status": "deleted"}

@router.get("/templates", response_model=List[PromptTemplate])
def list_templates(background_tasks: BackgroundTasks):
    return prompt_store.list_all(background_tasks)
