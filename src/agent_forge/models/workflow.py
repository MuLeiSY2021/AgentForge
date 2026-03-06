"""Workflow 与 WorkflowStep 数据模型。"""

from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class StepType(str, Enum):
    LLM_CALL = "llm_call"
    TOOL_CALL = "tool_call"
    HANDOFF = "handoff"
    REVIEW = "review"


class WorkflowStep(BaseModel):
    """工作流中的一步。"""

    id: UUID = Field(default_factory=uuid4)
    name: str
    step_type: StepType
    agent_id: UUID
    instruction: str = ""
    tool_name: str | None = None
    next_step_id: UUID | None = None


class Workflow(BaseModel):
    """线性/分支工作流定义。"""

    id: UUID = Field(default_factory=uuid4)
    name: str
    steps: list[WorkflowStep] = Field(default_factory=list)

    @property
    def first_step(self) -> WorkflowStep | None:
        return self.steps[0] if self.steps else None
