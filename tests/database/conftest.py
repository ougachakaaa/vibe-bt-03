from __future__ import annotations

import pytest

from vibe_bt_03.database.api import dispose_database


@pytest.fixture(autouse=True)
def clean_database_state() -> None:
    dispose_database()
    yield
    dispose_database()
