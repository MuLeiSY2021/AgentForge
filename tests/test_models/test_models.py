"""模型单元测试。"""

from uuid import UUID

from agent_forge.models.agent import Agent
from agent_forge.models.execution import ExecutionContext, ExecutionStatus, StepResult
from agent_forge.models.group import AgentGroup
from agent_forge.models.tool import ToolParameter, ToolSpec
from agent_forge.models.workflow import StepType, Workflow, WorkflowStep


def test_agent_creation() -> None:
    agent = Agent(name="coder", role="写代码")
    assert agent.name == "coder"
    assert isinstance(agent.id, UUID)
    assert agent.description_text == "coder: 写代码. "


def test_agent_serialization() -> None:
    agent = Agent(name="coder", role="写代码", tool_names=["web_search"])
    data = agent.model_dump_json()
    restored = Agent.model_validate_json(data)
    assert restored.name == agent.name
    assert restored.id == agent.id
    assert restored.tool_names == ["web_search"]


def test_group_creation() -> None:
    group = AgentGroup(name="research-team", description="做研究")
    assert group.name == "research-team"
    assert group.agent_ids == []


def test_workflow_steps() -> None:
    from uuid import uuid4

    aid = uuid4()
    step = WorkflowStep(name="step1", step_type=StepType.LLM_CALL, agent_id=aid)
    wf = Workflow(name="test-wf", steps=[step])
    assert wf.first_step is step
    assert len(wf.steps) == 1


def test_workflow_empty() -> None:
    wf = Workflow(name="empty")
    assert wf.first_step is None


def test_tool_spec_openai_function() -> None:
    spec = ToolSpec(
        name="search",
        description="搜索",
        parameters=[ToolParameter(name="q", type="string", description="关键词")],
    )
    fn = spec.to_openai_function()
    assert fn["type"] == "function"
    assert fn["function"]["name"] == "search"
    assert "q" in fn["function"]["parameters"]["properties"]


def test_execution_context_defaults() -> None:
    ctx = ExecutionContext(user_request="hello")
    assert ctx.status == ExecutionStatus.PENDING
    assert ctx.step_results == []


def test_step_result() -> None:
    from uuid import uuid4

    sr = StepResult(step_id=uuid4(), agent_id=uuid4(), output="done")
    assert sr.status == ExecutionStatus.COMPLETED
