"""OpenAI embedding 封装。"""

from __future__ import annotations

from openai import AsyncOpenAI

from agent_forge.config.settings import Settings


class EmbeddingClient:
    """调用 OpenAI embedding API 获取向量。"""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_embedding_model

    async def embed(self, text: str) -> list[float]:
        """对单条文本生成 embedding 向量。"""
        resp = await self._client.embeddings.create(model=self._model, input=text)
        return resp.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量生成 embedding 向量。"""
        if not texts:
            return []
        resp = await self._client.embeddings.create(model=self._model, input=texts)
        return [d.embedding for d in resp.data]
