from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from vibe_bt_03.database.api.manage import create_all_tables, reset_database


SchemaAction = Literal["initialize", "reset"]


@dataclass(frozen=True)
class SchemaChangeResult:
    action: SchemaAction
    completed: bool = True


@dataclass(frozen=True)
class InitializeDatabaseSchemaUseCase:
    create_tables: Callable[[], None] = create_all_tables

    def execute(self) -> SchemaChangeResult:
        self.create_tables()
        return SchemaChangeResult(action="initialize")


@dataclass(frozen=True)
class ResetDatabaseSchemaUseCase:
    reset_tables: Callable[[], None] = reset_database

    def execute(self) -> SchemaChangeResult:
        self.reset_tables()
        return SchemaChangeResult(action="reset")

