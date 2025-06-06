from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

class StoresInterface(ABC, Generic[T]):
    @abstractmethod
    def save(self, item: T) -> T:
        pass

    @abstractmethod
    def load(self, item_id: str) -> Optional[T]:
        pass

    @abstractmethod
    def update(self, item_id: str, item: T) -> T:
        pass

    @abstractmethod
    def delete(self, item_id: str) -> None:
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        pass

    @abstractmethod
    def list_summaries(self) -> List[dict]:
        pass
