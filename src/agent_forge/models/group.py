"""AgentGroup 数据模型。"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentGroup(BaseModel):
    """一组 Agent 的编排组合，可复用。"""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""
    agent_ids: list[UUID] = Field(default_factory=list)
    workflow_id: UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: list[float] | None = None

    @property
    def description_text(self) -> str:
        """用于 RAG embedding 的拼接文本。"""
        return f"{self.name}: {self.description}"
