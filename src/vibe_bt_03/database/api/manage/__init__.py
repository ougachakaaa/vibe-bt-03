"""Management-facing database APIs for CLI and admin tooling."""

from vibe_bt_03.database.api.manage.connection import (
    configure_database,
    database_transaction,
    dispose_database,
)
from vibe_bt_03.database.api.manage.health import (
    DatabaseHealth,
    check_database_connection,
    get_database_health,
)
from vibe_bt_03.database.api.manage.schema import create_all_tables, drop_all_tables, reset_database

__all__ = [
    "DatabaseHealth",
    "check_database_connection",
    "configure_database",
    "create_all_tables",
    "database_transaction",
    "dispose_database",
    "drop_all_tables",
    "get_database_health",
    "reset_database",
]
