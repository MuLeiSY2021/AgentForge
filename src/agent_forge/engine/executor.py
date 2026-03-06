"""WorkflowExecutor — 工作流执行引擎。"""

from __future__ import annotations

import json
import logging
from uuid import UUID

from agent_forge.engine.context import RuntimeContext
from agent_forge.models.execution import (
    ExecutionContext,
    ExecutionResult,
    ExecutionStatus,
    StepResult,
)
from agent_forge.models.workflow import StepType, Workflow

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """按步骤执行 Workflow，调度 Agent 和 Tool。"""

    def __init__(self, ctx: RuntimeContext) -> None:
        self._ctx = ctx

    async def execute(self, workflow: Workflow, exec_ctx: ExecutionContext) -> ExecutionResult:
        """执行整个 workflow，返回 ExecutionResult。"""
        exec_ctx.status = ExecutionStatus.RUNNING

        for step in workflow.steps:
            logger.info("Executing step: %s (%s)", step.name, step.step_type)

            try:
                output = await self._execute_step(step, exec_ctx)
                step_result = StepResult(
                    step_id=step.id,
                    agent_id=step.agent_id,
                    output=output,
                    status=ExecutionStatus.COMPLETED,
                )
            except Exception as e:
                logger.error("Step %s failed: %s", step.name, e)
                step_result = StepResult(
                    step_id=step.id,
                    agent_id=step.agent_id,
                    status=ExecutionStatus.FAILED,
                    error=str(e),
                )
                exec_ctx.step_results.append(step_result)
                exec_ctx.status = ExecutionStatus.FAILED
                return self._build_result(exec_ctx)

            exec_ctx.step_results.append(step_result)

        exec_ctx.status = ExecutionStatus.COMPLETED
        return self._build_result(exec_ctx)

    async def _execute_step(self, step, exec_ctx: ExecutionContext) -> str:
        """执行单步。"""
        agent = await self._ctx.agent_pool.get(step.agent_id)
        if agent is None:
            raise ValueError(f"Agent {step.agent_id} not found")

        # 构建对话上下文
        history = self._build_history(exec_ctx)
        messages = [
            {"role": "system", "content": agent.system_prompt or f"你是 {agent.name}，{agent.role}。"},
            *history,
            {"role": "user", "content": step.instruction or exec_ctx.user_request},
        ]

        if step.step_type == StepType.TOOL_CALL and step.tool_name:
            return await self._execute_tool_step(messages, step.tool_name, agent)
        else:
            # LLM_CALL / HANDOFF / REVIEW 都走普通 chat
            return await self._ctx.llm.chat(messages)

    async def _execute_tool_step(self, messages: list[dict], tool_name: str, agent) -> str:
        """执行带工具调用的步骤。"""
        tool = self._ctx.tool_registry.get(tool_name)
        if tool is None:
            raise ValueError(f"Tool {tool_name} not registered")

        tools_schema = [tool.spec.to_openai_function()]
        msg = await self._ctx.llm.chat_with_tools(messages, tools_schema)

        if msg.tool_calls:
            tc = msg.tool_calls[0]
            args = json.loads(tc.function.arguments)
            return await tool.execute(**args)

        return msg.content or ""

    def _build_history(self, exec_ctx: ExecutionContext) -> list[dict[str, str]]:
        """从已完成的步骤构建对话历史。"""
        history: list[dict[str, str]] = []
        for sr in exec_ctx.step_results:
            if sr.status == ExecutionStatus.COMPLETED:
                history.append({"role": "assistant", "content": sr.output})
        return history

    def _build_result(self, exec_ctx: ExecutionContext) -> ExecutionResult:
        final_output = ""
        if exec_ctx.step_results:
            last = exec_ctx.step_results[-1]
            final_output = last.output if last.status == ExecutionStatus.COMPLETED else last.error or ""
        return ExecutionResult(
            execution_id=exec_ctx.id,
            status=exec_ctx.status,
            final_output=final_output,
            step_results=exec_ctx.step_results,
        )
