"""ExecutionContext 和 ExecutionResult 数据模型。"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepResult(BaseModel):
    """单步执行结果。"""

    step_id: UUID
    agent_id: UUID
    output: str = ""
    status: ExecutionStatus = ExecutionStatus.COMPLETED
    error: str | None = None


class ExecutionContext(BaseModel):
    """一次工作流执行的上下文。"""

    id: UUID = Field(default_factory=uuid4)
    user_request: str
    group_id: UUID | None = None
    workflow_id: UUID | None = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    step_results: list[StepResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionResult(BaseModel):
    """最终执行结果。"""

    execution_id: UUID
    status: ExecutionStatus
    final_output: str = ""
    step_results: list[StepResult] = Field(default_factory=list)
