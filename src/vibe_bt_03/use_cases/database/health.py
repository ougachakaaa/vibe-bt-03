from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from vibe_bt_03.database.api.manage import check_database_connection


@dataclass(frozen=True)
class DatabaseHealthResult:
    healthy: bool


@dataclass(frozen=True)
class CheckDatabaseHealthUseCase:
    check_connection: Callable[[], bool] = check_database_connection

    def execute(self) -> DatabaseHealthResult:
        return DatabaseHealthResult(healthy=self.check_connection())

