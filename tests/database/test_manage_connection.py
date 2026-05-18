from __future__ import annotations

from sqlalchemy import select

from vibe_bt_03.config import DatabaseSettings
from vibe_bt_03.database.api import (
    check_database_connection,
    configure_database,
    create_all_tables,
    database_transaction,
    dispose_database,
)
from vibe_bt_03.database.api.manage import connection as connection_module
from vibe_bt_03.database.models.enums import AssetClass
from vibe_bt_03.database.models.instrument import Asset
from vibe_bt_03.database.session import session_scope


def test_configure_database_with_positional_url_enables_connection() -> None:
    configure_database("sqlite+pysqlite:///:memory:")

    assert check_database_connection() is True


def test_configure_database_with_database_url_keyword_enables_connection() -> None:
    configure_database(database_url="sqlite+pysqlite:///:memory:")

    assert check_database_connection() is True


def test_configure_database_accepts_database_settings(monkeypatch) -> None:
    captured: dict[str, object] = {}
    settings = DatabaseSettings()

    def fake_configure_database(
        received_settings,
        *,
        database_url=None,
        **engine_options,
    ) -> None:
        captured["settings"] = received_settings
        captured["database_url"] = database_url
        captured["engine_options"] = engine_options

    monkeypatch.setattr(connection_module, "_configure_database", fake_configure_database)

    connection_module.configure_database(settings, echo=True)

    assert captured == {
        "settings": settings,
        "database_url": None,
        "engine_options": {"echo": True},
    }


def test_dispose_database_clears_connection_state() -> None:
    configure_database("sqlite+pysqlite:///:memory:")
    assert check_database_connection() is True

    dispose_database()

    assert check_database_connection() is False


def test_database_transaction_commits_successful_work() -> None:
    configure_database("sqlite+pysqlite:///:memory:")
    create_all_tables()

    with database_transaction():
        with session_scope() as session:
            session.add(Asset(asset_class=AssetClass.STOCK, code="000001"))

    with session_scope() as session:
        asset = session.scalar(select(Asset).where(Asset.code == "000001"))

    assert asset is not None


def test_database_transaction_rolls_back_failed_work() -> None:
    configure_database("sqlite+pysqlite:///:memory:")
    create_all_tables()

    try:
        with database_transaction():
            with session_scope() as session:
                session.add(Asset(asset_class=AssetClass.STOCK, code="000001"))
            raise RuntimeError("force rollback")
    except RuntimeError:
        pass

    with session_scope() as session:
        asset = session.scalar(select(Asset).where(Asset.code == "000001"))

    assert asset is None
