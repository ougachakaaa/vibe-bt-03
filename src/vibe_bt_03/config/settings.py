from __future__ import annotations

import os
from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from vibe_bt_03.config.app import AppEnv, AppSettings
from vibe_bt_03.config.database import DatabaseSettings
from vibe_bt_03.config.datasource import DataSourceSettings
from vibe_bt_03.config.errors import ConfigError
from vibe_bt_03.config.ingestion import IngestionSettings
from vibe_bt_03.config.logging import LoggingSettings
from vibe_bt_03.config.paths import PathSettings


_ENV_ALIASES = {
    "dev": "development",
    "development": "development",
    "test": "testing",
    "testing": "testing",
    "prod": "production",
    "production": "production",
}


def normalize_env(env: str | None = None) -> AppEnv:
    raw = env or os.getenv("APP_ENV") or os.getenv("APP__ENV") or "development"
    normalized = _ENV_ALIASES.get(raw.lower())

    if normalized is None:
        raise ConfigError(f"Unsupported app environment: {raw}")

    return AppEnv(normalized)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    datasource: DataSourceSettings = Field(default_factory=DataSourceSettings)
    ingestion: IngestionSettings = Field(default_factory=IngestionSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    paths: PathSettings = Field(default_factory=PathSettings)

    @model_validator(mode="after")
    def validate_by_env(self) -> Settings:
        if self.app.env == AppEnv.PRODUCTION:
            if self.app.debug:
                raise ConfigError("DEBUG must be false in production")

            if self.database.password is None:
                raise ConfigError("DATABASE password is required in production")

        return self


def build_env_files(env: AppEnv) -> tuple[str, ...]:
    return (
        ".env",
        f".env.{env.value}",
        ".env.local",
    )


@lru_cache
def get_settings(env: str | None = None) -> Settings:
    app_env = normalize_env(env)
    env_files = build_env_files(app_env)

    return Settings(_env_file=env_files, app={"env": app_env})


def clear_settings_cache() -> None:
    get_settings.cache_clear()
