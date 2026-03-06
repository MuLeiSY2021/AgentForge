"""Web 搜索示例工具（stub 实现）。"""

from __future__ import annotations

from typing import Any

from agent_forge.models.tool import ToolParameter, ToolSpec
from agent_forge.tools.base import BaseTool


class WebSearchTool(BaseTool):
    """Web 搜索工具 — 当前为 stub，后续接入真实搜索 API。"""

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="web_search",
            description="搜索互联网获取相关信息。",
            parameters=[
                ToolParameter(name="query", type="string", description="搜索关键词"),
            ],
        )

    async def execute(self, **kwargs: Any) -> str:
        query = kwargs.get("query", "")
        return f"[stub] web_search results for: {query}"
