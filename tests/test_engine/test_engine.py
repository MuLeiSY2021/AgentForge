"""Engine 单元测试 — RuntimeContext 和 ToolRegistry。"""

from pathlib import Path

from agent_forge.config.settings import Settings
from agent_forge.engine.context import RuntimeContext
from agent_forge.tools.builtins.file_reader import FileReaderTool
from agent_forge.tools.builtins.web_search import WebSearchTool
from agent_forge.tools.registry import ToolRegistry


def test_runtime_context_creation(tmp_path: Path) -> None:
    settings = Settings(openai_api_key="test", storage_dir=tmp_path)
    ctx = RuntimeContext(settings)
    assert ctx.agent_pool is not None
    assert ctx.group_pool is not None
    assert ctx.tool_registry is not None
    assert "web_search" in ctx.tool_registry.list_names()
    assert "file_reader" in ctx.tool_registry.list_names()


def test_tool_registry() -> None:
    registry = ToolRegistry()
    registry.register(WebSearchTool())
    registry.register(FileReaderTool())

    assert len(registry.list_names()) == 2
    assert registry.get("web_search") is not None
    assert registry.get("nonexistent") is None

    specs = registry.list_specs()
    assert len(specs) == 2

    openai_tools = registry.get_openai_tools()
    assert len(openai_tools) == 2
    assert all(t["type"] == "function" for t in openai_tools)


def test_tool_registry_filtered() -> None:
    registry = ToolRegistry()
    registry.register(WebSearchTool())
    registry.register(FileReaderTool())

    tools = registry.get_openai_tools(["web_search"])
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "web_search"
