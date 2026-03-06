"""MetaAgent — 系统大脑，负责匹配/创建 Agent 和工作流。"""

from __future__ import annotations

import logging
from uuid import UUID

from pydantic import BaseModel, Field

from agent_forge.engine.context import RuntimeContext
from agent_forge.models.agent import Agent
from agent_forge.models.execution import ExecutionContext, ExecutionResult
from agent_forge.models.group import AgentGroup
from agent_forge.models.workflow import StepType, Workflow, WorkflowStep

logger = logging.getLogger(__name__)


# --- Structured output schemas for LLM ---


class PlannedAgent(BaseModel):
    """LLM 规划的单个 Agent。"""

    name: str
    role: str
    backstory: str = ""
    system_prompt: str = ""
    tool_names: list[str] = Field(default_factory=list)


class PlannedStep(BaseModel):
    """LLM 规划的单个步骤。"""

    name: str
    step_type: StepType
    agent_name: str
    instruction: str = ""
    tool_name: str | None = None


class WorkflowPlan(BaseModel):
    """LLM 规划的完整工作流。"""

    group_name: str
    group_description: str = ""
    agents: list[PlannedAgent]
    steps: list[PlannedStep]


PLAN_PROMPT = """\
你是 AgentForge 的规划者。用户提出了一个需求，请规划一组 Agent 和工作流来完成。

可用工具：{tool_names}

用户需求：{user_request}

请规划：
1. 需要哪些 Agent（名称、角色、系统提示词、需要的工具）
2. 工作流步骤（每步用哪个 Agent、做什么、类型是 llm_call/tool_call/handoff/review）

注意：step_type 只能是 llm_call, tool_call, handoff, review 之一。
tool_name 只在 step_type 为 tool_call 时设置，且必须是可用工具中的一个。
"""


class MetaAgent:
    """系统大脑 — RAG 匹配已有 Group，或规划创建新的。"""

    def __init__(self, ctx: RuntimeContext) -> None:
        self._ctx = ctx

    async def handle_request(self, user_request: str) -> ExecutionResult:
        """处理用户请求的主入口。"""
        # 1. 尝试 RAG 匹配已有 Group
        group = await self._match_group(user_request)

        if group is None:
            # 2. 没有匹配到，让 LLM 规划并创建
            logger.info("No matching group found, planning new workflow...")
            group = await self._plan_and_create(user_request)

        # 3. 执行工作流
        return await self._execute_group(group, user_request)

    async def _match_group(self, query: str) -> AgentGroup | None:
        """通过 RAG 在 Group 池中查找最匹配的。"""
        groups = await self._ctx.group_pool.list_all()
        if not groups:
            return None

        results = await self._ctx.retriever.find_similar(
            query=query,
            candidates=groups,
            get_embedding=lambda g: g.embedding,
            get_text=lambda g: g.description_text,
            top_k=1,
            threshold=0.75,
        )

        if results:
            group, score = results[0]
            logger.info("Matched group '%s' with score %.3f", group.name, score)
            return group
        return None

    async def _plan_and_create(self, user_request: str) -> AgentGroup:
        """让 LLM 规划工作流，创建 Agent 和 Group 并存入池。"""
        tool_names = ", ".join(self._ctx.tool_registry.list_names()) or "无"
        messages = [
            {
                "role": "user",
                "content": PLAN_PROMPT.format(
                    tool_names=tool_names,
                    user_request=user_request,
                ),
            }
        ]

        plan = await self._ctx.llm.chat_structured(messages, WorkflowPlan, temperature=0.5)

        # 创建 Agents
        name_to_id: dict[str, UUID] = {}
        agent_ids: list[UUID] = []
        for pa in plan.agents:
            agent = Agent(
                name=pa.name,
                role=pa.role,
                backstory=pa.backstory,
                system_prompt=pa.system_prompt,
                tool_names=pa.tool_names,
            )
            # 生成 embedding 用于后续 RAG
            emb = await self._ctx.embedding_client.embed(agent.description_text)
            agent.embedding = emb
            await self._ctx.agent_pool.add(agent)
            name_to_id[pa.name] = agent.id
            agent_ids.append(agent.id)

        # 创建 Workflow
        steps: list[WorkflowStep] = []
        for ps in plan.steps:
            agent_id = name_to_id.get(ps.agent_name)
            if agent_id is None:
                logger.warning("Agent '%s' not found in plan, skipping step", ps.agent_name)
                continue
            steps.append(
                WorkflowStep(
                    name=ps.name,
                    step_type=ps.step_type,
                    agent_id=agent_id,
                    instruction=ps.instruction,
                    tool_name=ps.tool_name,
                )
            )

        workflow = Workflow(name=f"workflow-{plan.group_name}", steps=steps)

        # 创建 Group
        group = AgentGroup(
            name=plan.group_name,
            description=plan.group_description,
            agent_ids=agent_ids,
            workflow_id=workflow.id,
        )
        # 生成 Group embedding
        emb = await self._ctx.embedding_client.embed(group.description_text)
        group.embedding = emb
        await self._ctx.group_pool.add(group)

        # 存储 workflow
        await self._ctx.storage.save("workflows", workflow.id, workflow)

        logger.info(
            "Created group '%s' with %d agents, %d steps",
            group.name,
            len(agent_ids),
            len(steps),
        )
        return group

    async def _execute_group(self, group: AgentGroup, user_request: str) -> ExecutionResult:
        """加载 group 的 workflow 并执行。"""
        from agent_forge.engine.executor import WorkflowExecutor
        from agent_forge.models.workflow import Workflow as WorkflowModel

        if group.workflow_id is None:
            raise ValueError(f"Group '{group.name}' has no workflow")

        workflow = await self._ctx.storage.load("workflows", group.workflow_id, WorkflowModel)
        if workflow is None:
            raise ValueError(f"Workflow {group.workflow_id} not found")

        exec_ctx = ExecutionContext(
            user_request=user_request,
            group_id=group.id,
            workflow_id=workflow.id,
        )

        executor = WorkflowExecutor(self._ctx)
        return await executor.execute(workflow, exec_ctx)
