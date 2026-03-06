"""Agent 数据模型。"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Agent(BaseModel):
    """池中的一个 Agent 定义。"""

    id: UUID = Field(default_factory=uuid4)
    name: str
    role: str = ""
    backstory: str = ""
    system_prompt: str = ""
    tool_names: list[str] = Field(default_factory=list)
    model: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: list[float] | None = None

    @property
    def description_text(self) -> str:
        """用于 RAG embedding 的拼接文本。"""
        return f"{self.name}: {self.role}. {self.backstory}"
