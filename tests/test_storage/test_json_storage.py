"""Storage 单元测试。"""

import pytest

from agent_forge.models.agent import Agent
from agent_forge.storage.json_storage import JsonStorage


@pytest.mark.asyncio
async def test_save_and_load(tmp_storage: JsonStorage) -> None:
    agent = Agent(name="test", role="tester")
    await tmp_storage.save("agents", agent.id, agent)
    loaded = await tmp_storage.load("agents", agent.id, Agent)
    assert loaded is not None
    assert loaded.name == "test"
    assert loaded.id == agent.id


@pytest.mark.asyncio
async def test_load_nonexistent(tmp_storage: JsonStorage) -> None:
    from uuid import uuid4

    result = await tmp_storage.load("agents", uuid4(), Agent)
    assert result is None


@pytest.mark.asyncio
async def test_load_all(tmp_storage: JsonStorage) -> None:
    a1 = Agent(name="a1", role="r1")
    a2 = Agent(name="a2", role="r2")
    await tmp_storage.save("agents", a1.id, a1)
    await tmp_storage.save("agents", a2.id, a2)
    all_agents = await tmp_storage.load_all("agents", Agent)
    assert len(all_agents) == 2


@pytest.mark.asyncio
async def test_delete(tmp_storage: JsonStorage) -> None:
    agent = Agent(name="del", role="deletable")
    await tmp_storage.save("agents", agent.id, agent)
    assert await tmp_storage.exists("agents", agent.id)
    ok = await tmp_storage.delete("agents", agent.id)
    assert ok
    assert not await tmp_storage.exists("agents", agent.id)


@pytest.mark.asyncio
async def test_delete_nonexistent(tmp_storage: JsonStorage) -> None:
    from uuid import uuid4

    ok = await tmp_storage.delete("agents", uuid4())
    assert not ok


@pytest.mark.asyncio
async def test_load_all_empty(tmp_storage: JsonStorage) -> None:
    result = await tmp_storage.load_all("nonexistent", Agent)
    assert result == []
