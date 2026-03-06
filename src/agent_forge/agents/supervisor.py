"""SupervisorAgent — 监督工作流执行质量。"""

from __future__ import annotations

import logging

from agent_forge.engine.context import RuntimeContext
from agent_forge.models.execution import ExecutionResult, ExecutionStatus

logger = logging.getLogger(__name__)

REVIEW_PROMPT = """\
你是 AgentForge 的质量监督者。请审查以下工作流执行结果，判断是否满足用户需求。

用户需求：{user_request}

执行结果：
{execution_summary}

请回答：
1. 结果是否满足用户需求？(是/否)
2. 如果不满足，哪些方面需要改进？
3. 给出 1-10 的质量评分。

请用 JSON 格式回答：{{"satisfied": true/false, "feedback": "...", "score": N}}
"""


class SupervisorAgent:
    """监督 Agent — 审查工作流执行结果的质量。"""

    def __init__(self, ctx: RuntimeContext) -> None:
        self._ctx = ctx

    async def review(self, user_request: str, result: ExecutionResult) -> dict:
        """审查执行结果，返回评审意见。"""
        if result.status == ExecutionStatus.FAILED:
            return {
                "satisfied": False,
                "feedback": f"执行失败: {result.final_output}",
                "score": 0,
            }

        summary = self._build_summary(result)
        messages = [
            {
                "role": "user",
                "content": REVIEW_PROMPT.format(
                    user_request=user_request,
                    execution_summary=summary,
                ),
            }
        ]

        import json

        raw = await self._ctx.llm.chat(messages, temperature=0.3)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Supervisor returned non-JSON: %s", raw)
            return {"satisfied": True, "feedback": raw, "score": 5}

    def _build_summary(self, result: ExecutionResult) -> str:
        lines: list[str] = []
        for i, sr in enumerate(result.step_results, 1):
            status = "OK" if sr.status == ExecutionStatus.COMPLETED else "FAIL"
            output = sr.output[:200] if sr.output else sr.error or ""
            lines.append(f"Step {i} [{status}]: {output}")
        return "\n".join(lines)
