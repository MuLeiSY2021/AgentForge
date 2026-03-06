"""余弦相似度检索器。"""

from __future__ import annotations

from typing import TypeVar

import numpy as np
from pydantic import BaseModel

from agent_forge.rag.embeddings import EmbeddingClient

T = TypeVar("T", bound=BaseModel)


class Retriever:
    """基于余弦相似度的向量检索器。"""

    def __init__(self, embedding_client: EmbeddingClient) -> None:
        self._embedding_client = embedding_client

    async def find_similar(
        self,
        query: str,
        candidates: list[T],
        get_embedding: callable,
        get_text: callable,
        top_k: int = 3,
        threshold: float = 0.5,
    ) -> list[tuple[T, float]]:
        """在 candidates 中找到与 query 最相似的 top_k 个。

        Args:
            query: 用户查询文本
            candidates: 候选对象列表
            get_embedding: 从对象取已有 embedding 的函数 (obj) -> list[float] | None
            get_text: 从对象取文本的函数 (obj) -> str，用于生成缺失的 embedding
            top_k: 返回前 k 个
            threshold: 相似度阈值

        Returns:
            (候选对象, 相似度分数) 列表，按分数降序
        """
        if not candidates:
            return []

        # 为缺少 embedding 的候选生成向量
        texts_to_embed: list[tuple[int, str]] = []
        for i, c in enumerate(candidates):
            if get_embedding(c) is None:
                texts_to_embed.append((i, get_text(c)))

        if texts_to_embed:
            indices, texts = zip(*texts_to_embed)
            embeddings = await self._embedding_client.embed_batch(list(texts))
            for idx, emb in zip(indices, embeddings):
                # 注意：这里不修改原对象，仅缓存到本次搜索
                candidates[idx] = candidates[idx].model_copy(update={"embedding": emb})

        # 获取 query embedding
        query_emb = np.array(await self._embedding_client.embed(query))

        # 计算余弦相似度
        results: list[tuple[T, float]] = []
        for c in candidates:
            emb = get_embedding(c)
            if emb is None:
                continue
            c_emb = np.array(emb)
            similarity = float(np.dot(query_emb, c_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(c_emb) + 1e-10))
            if similarity >= threshold:
                results.append((c, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
