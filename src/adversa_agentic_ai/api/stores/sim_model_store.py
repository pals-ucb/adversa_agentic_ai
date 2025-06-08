# File: src/api/stores/model_store.py
import os
from uuid import UUID
from fastapi import BackgroundTasks
from typing import Dict, List
from ..schemas.sim_models import SimModel
#from .file_store import FileStore
from .s3_store import S3Store



class SimModelStore:
    def __init__(self):
        self._store: Dict[str, SimModel] = {}
        # self._pstore = FileStore[SimModel]("data/sim_models", SimModel) # Persistent filestore
        # The bucket and prefix can be overridden by environment variables in Lambda
        BUCKET = os.getenv("DATA_BUCKET", "adversa-agentic-ai-data")
        PREFIX = os.getenv("SIM_MODELS_PREFIX", "sim_models")
        self._s3store = S3Store[SimModel](bucket=BUCKET, prefix=PREFIX, model_cls=SimModel)

    def save(self, model: SimModel, background_tasks: BackgroundTasks) -> SimModel:
        self._store[model.id] = model
        #background_tasks.add_task(self._pstore.save, model)
        #background_tasks.add_task(self._s3store.save, model)
        self._s3store.save(model)
        return model

    def get(self, model_id: str) -> SimModel | None:
        if model_id in self._store:
            return self._store[model_id]
        # Lazy load from file
        model = self._s3store.load(model_id)
        if model:
            self._store[model_id] = model
            return model
        return None
        

    def update(self, model_id: str, updated_model: SimModel, background_tasks: BackgroundTasks) -> SimModel:
        self._store[model_id] = updated_model
        #background_tasks.add_task(self._pstore.save, updated_model)
        #background_tasks.add_task(self._s3store.save, updated_model)
        self._s3store.save(updated_model)
        return updated_model

    def delete(self, model_id: str, background_tasks: BackgroundTasks) -> None:
        if model_id in self._store:
            del self._store[model_id]
        #background_tasks.add_task(self._pstore.delete, model_id)
        #background_tasks.add_task(self._s3store.delete, model_id)
        self._s3store.delete(model)

    def list_all(self, background_tasks: BackgroundTasks) -> List[SimModel]:
        return list(self._store.values())

    def list_summaries(self, background_tasks: BackgroundTasks) -> List[dict]:
        return [{"id": m.id, "name": m.name} for m in self._store.values()]
