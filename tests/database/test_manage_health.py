from __future__ import annotations

from vibe_bt_03.database.api import (
    check_database_connection,
    configure_database,
    get_database_health,
)


def test_get_database_health_reports_unconfigured_database() -> None:
    health = get_database_health()

    assert health.ok is False
    assert health.error is not None
    assert check_database_connection() is False


def test_get_database_health_reports_successful_connection() -> None:
    configure_database("sqlite+pysqlite:///:memory:")

    health = get_database_health()

    assert health.ok is True
    assert health.dialect == "sqlite"
    assert health.driver == "pysqlite"
    assert health.url_masked == "sqlite+pysqlite:///:memory:"
    assert health.error is None
    assert check_database_connection() is True


def test_get_database_health_reports_failed_connection(tmp_path) -> None:
    missing_parent = tmp_path / "missing-parent"
    database_path = missing_parent / "db.sqlite"
    configure_database(f"sqlite+pysqlite:///{database_path.as_posix()}")

    health = get_database_health()

    assert health.ok is False
    assert health.error is not None
    assert "OperationalError" in health.error
    assert check_database_connection() is False
