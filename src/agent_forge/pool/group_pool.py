"""Group 池 CRUD 操作。"""

from __future__ import annotations

from uuid import UUID

from agent_forge.models.group import AgentGroup
from agent_forge.storage.base import StorageBackend

COLLECTION = "groups"


class GroupPool:
    """AgentGroup 池 — 管理所有 Group 的增删改查。"""

    def __init__(self, storage: StorageBackend) -> None:
        self._storage = storage

    async def add(self, group: AgentGroup) -> AgentGroup:
        await self._storage.save(COLLECTION, group.id, group)
        return group

    async def get(self, id: UUID) -> AgentGroup | None:
        return await self._storage.load(COLLECTION, id, AgentGroup)

    async def list_all(self) -> list[AgentGroup]:
        return await self._storage.load_all(COLLECTION, AgentGroup)

    async def delete(self, id: UUID) -> bool:
        return await self._storage.delete(COLLECTION, id)

    async def update(self, group: AgentGroup) -> AgentGroup:
        await self._storage.save(COLLECTION, group.id, group)
        return group
