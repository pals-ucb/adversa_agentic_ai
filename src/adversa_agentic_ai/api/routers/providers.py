from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.providers import Provider
from ..stores.provider_store import ProviderStore

router = APIRouter(
    prefix="/providers",
    tags=["Providers"],
    responses={404: {"description": "Provider not found"}}
)

provider_db = ProviderStore()

@router.post(
    "",
    response_model=Provider,
    summary="Create a new provider",
    description="Registers a new model provider along with platform and credential configuration."
)
def create_provider(provider: Provider):
    if provider_db.get(provider.id):
        raise HTTPException(status_code=400, detail="Provider already exists")
    return provider_db.save(provider)

@router.get(
    "/{provider_id}",
    response_model=Provider,
    summary="Get a provider",
    description="Fetches a provider by its unique ID, including platform details."
)
def get_provider(provider_id: str):
    provider = provider_db.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.put(
    "/{provider_id}",
    response_model=Provider,
    summary="Update a provider",
    description="Updates an existing provider’s information, including its credential profile and platforms."
)
def update_provider(provider_id: str, provider: Provider):
    if not provider_db.get(provider_id):
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider_db.update(provider_id, provider)

@router.delete(
    "/{provider_id}",
    summary="Delete a provider",
    description="Removes a provider and its associated configuration from the system."
)
def delete_provider(provider_id: str):
    if not provider_db.get(provider_id):
        raise HTTPException(status_code=404, detail="Provider not found")
    provider_db.delete(provider_id)
    return {"status": "deleted"}

@router.get(
    "",
    response_model=List[Provider],
    summary="List all providers",
    description="Returns a list of all configured providers and their supported platforms."
)
def list_providers():
    return provider_db.list_all()
