from __future__ import annotations

import pytest

from vibe_bt_03.config import AppEnv, clear_settings_cache, get_settings, normalize_env
from vibe_bt_03.config.errors import ConfigError


CONFIG_ENV_NAMES = (
    "APP_ENV",
    "APP__ENV",
    "APP__DEBUG",
    "DATABASE__HOST",
    "DATABASE__PASSWORD",
)


def clear_config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in CONFIG_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_default_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)
    clear_settings_cache()

    settings = get_settings()

    assert settings.app.env == AppEnv.DEVELOPMENT
    assert settings.database.host == "localhost"
    assert settings.ingestion.stock_bar_start_date.isoformat() == "2010-01-01"


def test_normalize_env_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)

    assert normalize_env("dev") == AppEnv.DEVELOPMENT
    assert normalize_env("test") == AppEnv.TESTING
    assert normalize_env("prod") == AppEnv.PRODUCTION


def test_invalid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)

    with pytest.raises(ConfigError):
        normalize_env("staging")


def test_env_override_database_host(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)
    clear_settings_cache()
    monkeypatch.setenv("DATABASE__HOST", "127.0.0.1")

    settings = get_settings()

    assert settings.database.host == "127.0.0.1"


def test_secret_str_masked(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)
    clear_settings_cache()
    monkeypatch.setenv("DATABASE__PASSWORD", "secret")

    settings = get_settings()

    assert settings.database.password is not None
    assert "secret" not in repr(settings.database.password)
    assert settings.database.password.get_secret_value() == "secret"


def test_production_debug_not_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)
    clear_settings_cache()
    monkeypatch.setenv("APP__DEBUG", "true")
    monkeypatch.setenv("DATABASE__PASSWORD", "secret")

    with pytest.raises(ConfigError):
        get_settings("prod")


def test_database_url_with_password(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_config_env(monkeypatch)
    clear_settings_cache()
    monkeypatch.setenv("DATABASE__PASSWORD", "123456")

    settings = get_settings()

    assert settings.database.url == "postgresql+psycopg://postgres:123456@localhost:5432/vibe_bt"
