# File: src/api/stores/model_store.py
from typing import Dict, List
from ..schemas.sim_models import SimModel

class SimModelStore:
    def __init__(self):
        self._store: Dict[str, SimModel] = {}

    def save(self, model: SimModel) -> SimModel:
        self._store[model.id] = model
        return model

    def get(self, model_id: str) -> SimModel | None:
        return self._store.get(model_id)

    def update(self, model_id: str, updated: SimModel) -> SimModel:
        self._store[model_id] = updated
        return updated

    def delete(self, model_id: str) -> None:
        if model_id in self._store:
            del self._store[model_id]

    def list_all(self) -> List[SimModel]:
        return list(self._store.values())

    def list_summaries(self) -> List[dict]:
        return [{"id": m.id, "name": m.name} for m in self._store.values()]
