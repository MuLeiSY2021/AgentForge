"""RuntimeContext — 组合根，手动依赖注入。"""

from __future__ import annotations

from agent_forge.config.settings import Settings
from agent_forge.llm.client import LLMClient
from agent_forge.pool.agent_pool import AgentPool
from agent_forge.pool.group_pool import GroupPool
from agent_forge.rag.embeddings import EmbeddingClient
from agent_forge.rag.retriever import Retriever
from agent_forge.storage.json_storage import JsonStorage
from agent_forge.tools.builtins import FileReaderTool, WebSearchTool
from agent_forge.tools.registry import ToolRegistry


class RuntimeContext:
    """应用组合根 — 持有所有核心依赖的单一入口。"""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

        # Storage
        self.storage = JsonStorage(self.settings.storage_dir)

        # LLM
        self.llm = LLMClient(self.settings)

        # Pools
        self.agent_pool = AgentPool(self.storage)
        self.group_pool = GroupPool(self.storage)

        # RAG
        self.embedding_client = EmbeddingClient(self.settings)
        self.retriever = Retriever(self.embedding_client)

        # Tools
        self.tool_registry = ToolRegistry()
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        self.tool_registry.register(WebSearchTool())
        self.tool_registry.register(FileReaderTool())
