"""抽象 StorageBackend 接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class StorageBackend(ABC):
    """持久化存储的抽象基类。"""

    @abstractmethod
    async def save(self, collection: str, id: UUID, data: BaseModel) -> None: ...

    @abstractmethod
    async def load(self, collection: str, id: UUID, model_class: type[T]) -> T | None: ...

    @abstractmethod
    async def load_all(self, collection: str, model_class: type[T]) -> list[T]: ...

    @abstractmethod
    async def delete(self, collection: str, id: UUID) -> bool: ...

    @abstractmethod
    async def exists(self, collection: str, id: UUID) -> bool: ...
