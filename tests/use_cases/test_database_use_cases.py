from __future__ import annotations

from vibe_bt_03.use_cases.database import (
    CheckDatabaseHealthUseCase,
    InitializeDatabaseSchemaUseCase,
    ResetDatabaseSchemaUseCase,
)


def test_check_database_health_use_case_uses_injected_checker() -> None:
    use_case = CheckDatabaseHealthUseCase(check_connection=lambda: True)

    result = use_case.execute()

    assert result.healthy is True


def test_initialize_database_schema_use_case_calls_create_tables() -> None:
    calls: list[str] = []
    use_case = InitializeDatabaseSchemaUseCase(create_tables=lambda: calls.append("create"))

    result = use_case.execute()

    assert calls == ["create"]
    assert result.action == "initialize"
    assert result.completed is True


def test_reset_database_schema_use_case_calls_reset_tables() -> None:
    calls: list[str] = []
    use_case = ResetDatabaseSchemaUseCase(reset_tables=lambda: calls.append("reset"))

    result = use_case.execute()

    assert calls == ["reset"]
    assert result.action == "reset"
    assert result.completed is True

