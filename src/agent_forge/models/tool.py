"""ToolSpec 序列化模型 — 与 BaseTool 可执行代码解耦。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """工具参数描述。"""

    name: str
    type: str = "string"
    description: str = ""
    required: bool = True


class ToolSpec(BaseModel):
    """工具的元数据，用于序列化存储和 LLM function-calling schema 生成。"""

    name: str
    description: str = ""
    parameters: list[ToolParameter] = Field(default_factory=list)

    def to_openai_function(self) -> dict:
        """转换为 OpenAI function-calling 的 JSON schema。"""
        properties: dict = {}
        required: list[str] = []
        for p in self.parameters:
            properties[p.name] = {"type": p.type, "description": p.description}
            if p.required:
                required.append(p.name)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
