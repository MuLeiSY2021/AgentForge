"""文件读取示例工具。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_forge.models.tool import ToolParameter, ToolSpec
from agent_forge.tools.base import BaseTool


class FileReaderTool(BaseTool):
    """读取本地文件内容。"""

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="file_reader",
            description="读取指定路径的文件内容。",
            parameters=[
                ToolParameter(name="path", type="string", description="文件路径"),
            ],
        )

    async def execute(self, **kwargs: Any) -> str:
        path_str = kwargs.get("path", "")
        path = Path(path_str)
        if not path.exists():
            return f"Error: file not found: {path_str}"
        if not path.is_file():
            return f"Error: not a file: {path_str}"
        return path.read_text(encoding="utf-8")
