from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.providers import Provider
from ..stores.provider_store import ProviderStore

router = APIRouter()
provider_db = ProviderStore()

@router.post("/providers", response_model=Provider)
def create_provider(provider: Provider):
    if provider_db.get(provider.id):
        raise HTTPException(status_code=400, detail="Provider already exists")
    return provider_db.save(provider)

@router.get("/providers/{provider_id}", response_model=Provider)
def get_provider(provider_id: str):
    provider = provider_db.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.put("/providers/{provider_id}", response_model=Provider)
def update_provider(provider_id: str, provider: Provider):
    if not provider_db.get(provider_id):
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider_db.update(provider_id, provider)

@router.delete("/providers/{provider_id}")
def delete_provider(provider_id: str):
    if not provider_db.get(provider_id):
        raise HTTPException(status_code=404, detail="Provider not found")
    provider_db.delete(provider_id)
    return {"status": "deleted"}

@router.get("/providers", response_model=List[Provider])
def list_providers():
    return provider_db.list_all()
