from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class AppEnv(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class AppSettings(BaseModel):
    name: str = "vibe-bt"
    env: AppEnv = AppEnv.DEVELOPMENT
    debug: bool = True
    timezone: str = "Asia/Shanghai"
