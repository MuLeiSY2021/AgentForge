"""Pool 单元测试。"""

import pytest

from agent_forge.models.agent import Agent
from agent_forge.models.group import AgentGroup
from agent_forge.pool.agent_pool import AgentPool
from agent_forge.pool.group_pool import GroupPool
from agent_forge.storage.json_storage import JsonStorage


@pytest.mark.asyncio
async def test_agent_pool_crud(tmp_storage: JsonStorage) -> None:
    pool = AgentPool(tmp_storage)

    # Add
    agent = Agent(name="test", role="tester")
    created = await pool.add(agent)
    assert created.id == agent.id

    # Get
    loaded = await pool.get(agent.id)
    assert loaded is not None
    assert loaded.name == "test"

    # List
    all_agents = await pool.list_all()
    assert len(all_agents) == 1

    # Update
    agent.role = "senior tester"
    await pool.update(agent)
    updated = await pool.get(agent.id)
    assert updated is not None
    assert updated.role == "senior tester"

    # Delete
    ok = await pool.delete(agent.id)
    assert ok
    assert await pool.get(agent.id) is None


@pytest.mark.asyncio
async def test_group_pool_crud(tmp_storage: JsonStorage) -> None:
    pool = GroupPool(tmp_storage)

    group = AgentGroup(name="team", description="test team")
    await pool.add(group)

    loaded = await pool.get(group.id)
    assert loaded is not None
    assert loaded.name == "team"

    all_groups = await pool.list_all()
    assert len(all_groups) == 1

    await pool.delete(group.id)
    assert await pool.get(group.id) is None
