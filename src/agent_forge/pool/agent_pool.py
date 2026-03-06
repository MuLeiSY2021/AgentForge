"""Agent 池 CRUD 操作。"""

from __future__ import annotations

from uuid import UUID

from agent_forge.models.agent import Agent
from agent_forge.storage.base import StorageBackend

COLLECTION = "agents"


class AgentPool:
    """Agent 池 — 管理所有 Agent 的增删改查。"""

    def __init__(self, storage: StorageBackend) -> None:
        self._storage = storage

    async def add(self, agent: Agent) -> Agent:
        await self._storage.save(COLLECTION, agent.id, agent)
        return agent

    async def get(self, id: UUID) -> Agent | None:
        return await self._storage.load(COLLECTION, id, Agent)

    async def list_all(self) -> list[Agent]:
        return await self._storage.load_all(COLLECTION, Agent)

    async def delete(self, id: UUID) -> bool:
        return await self._storage.delete(COLLECTION, id)

    async def update(self, agent: Agent) -> Agent:
        await self._storage.save(COLLECTION, agent.id, agent)
        return agent
