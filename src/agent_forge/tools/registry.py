"""ToolRegistry — 工具注册中心。"""

from __future__ import annotations

from agent_forge.models.tool import ToolSpec
from agent_forge.tools.base import BaseTool


class ToolRegistry:
    """全局工具注册表，管理所有可用工具。"""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_specs(self) -> list[ToolSpec]:
        return [t.spec for t in self._tools.values()]

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def get_openai_tools(self, names: list[str] | None = None) -> list[dict]:
        """返回 OpenAI function-calling 格式的工具列表。"""
        targets = names or list(self._tools.keys())
        return [self._tools[n].spec.to_openai_function() for n in targets if n in self._tools]
