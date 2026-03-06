"""共享 fixtures。"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_forge.config.settings import Settings
from agent_forge.storage.json_storage import JsonStorage


@pytest.fixture
def tmp_storage(tmp_path: Path) -> JsonStorage:
    return JsonStorage(tmp_path)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(openai_api_key="test-key", storage_dir=tmp_path)
