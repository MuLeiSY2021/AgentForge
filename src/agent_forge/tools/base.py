"""BaseTool 抽象类 — 可执行工具的接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agent_forge.models.tool import ToolSpec


class BaseTool(ABC):
    """所有可执行工具的基类。"""

    @property
    @abstractmethod
    def spec(self) -> ToolSpec:
        """返回工具的元数据描述。"""
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """执行工具，返回字符串结果。"""
        ...

    @property
    def name(self) -> str:
        return self.spec.name
