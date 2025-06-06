import os
import json
from typing import Type, TypeVar, Generic, List, Optional
from uuid import UUID
from pydantic import BaseModel
from .stores_interface import StoresInterface

T = TypeVar("T", bound=BaseModel)

class FileStore(StoresInterface[T], Generic[T]):
    def __init__(self, base_path: str, model_class: Type[T]):
        self.base_path = base_path
        self.model_class = model_class
        os.makedirs(base_path, exist_ok=True)

    def _file_path(self, item_id: str) -> str:
        return os.path.join(self.base_path, f"{item_id}.json")

    def save(self, item: T) -> T:
        path = self._file_path(str(item.id))
        with open(path, "w") as f:
            f.write(item.model_dump_json(indent=2)) 
        return item

    def load(self, item_id: str) -> Optional[T]:
        path = self._file_path(item_id)
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            data = json.load(f)
            return self.model_class(**data)

    def update(self, item_id: str, item: T) -> T:
        return self.save(item)

    def delete(self, item_id: str) -> None:
        path = self._file_path(item_id)
        if os.path.exists(path):
            os.remove(path)

    def list_all(self) -> List[T]:
        items = []
        for filename in os.listdir(self.base_path):
            if filename.endswith(".json"):
                with open(os.path.join(self.base_path, filename), "r") as f:
                    data = json.load(f)
                    items.append(self.model_class(**data))
        return items

    def list_summaries(self) -> List[dict]:
        return [{"id": str(item.id), "name": getattr(item, "name", "")}
                for item in self.list_all()]
