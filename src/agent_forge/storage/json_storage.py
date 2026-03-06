"""JSON 文件存储实现。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel

from agent_forge.storage.base import StorageBackend

T = TypeVar("T", bound=BaseModel)


class JsonStorage(StorageBackend):
    """基于 JSON 文件的存储后端，每个对象一个文件。"""

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir

    def _path(self, collection: str, id: UUID) -> Path:
        d = self._base_dir / collection
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{id}.json"

    async def save(self, collection: str, id: UUID, data: BaseModel) -> None:
        path = self._path(collection, id)
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    async def load(self, collection: str, id: UUID, model_class: type[T]) -> T | None:
        path = self._path(collection, id)
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        return model_class.model_validate(raw)

    async def load_all(self, collection: str, model_class: type[T]) -> list[T]:
        d = self._base_dir / collection
        if not d.exists():
            return []
        items: list[T] = []
        for f in sorted(d.glob("*.json")):
            raw = json.loads(f.read_text(encoding="utf-8"))
            items.append(model_class.model_validate(raw))
        return items

    async def delete(self, collection: str, id: UUID) -> bool:
        path = self._path(collection, id)
        if path.exists():
            path.unlink()
            return True
        return False

    async def exists(self, collection: str, id: UUID) -> bool:
        return self._path(collection, id).exists()
