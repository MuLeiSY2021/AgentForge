"""Async OpenAI 客户端封装。"""

from __future__ import annotations

from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from agent_forge.config.settings import Settings

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """对 AsyncOpenAI 的轻量封装，提供 chat 和 structured output。"""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> str:
        """普通 chat completion，返回 assistant 文本。"""
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        resp = await self._client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    async def chat_structured(
        self,
        messages: list[dict[str, str]],
        response_format: type[T],
        *,
        temperature: float = 0.7,
    ) -> T:
        """使用 OpenAI structured output 返回 Pydantic 对象。"""
        resp = await self._client.beta.chat.completions.parse(
            model=self._model,
            messages=messages,
            response_format=response_format,
            temperature=temperature,
        )
        parsed = resp.choices[0].message.parsed
        if parsed is None:
            raise ValueError("LLM returned empty structured output")
        return parsed

    async def chat_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict],
        *,
        temperature: float = 0.7,
    ) -> Any:
        """带 tool_calls 的 chat，返回完整 message 对象。"""
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools,
            temperature=temperature,
        )
        return resp.choices[0].message
