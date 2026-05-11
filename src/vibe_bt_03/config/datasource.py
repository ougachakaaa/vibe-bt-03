from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, SecretStr, field_validator


class DataSourceSettings(BaseModel):
    primary_stock_datasource: str = "tushare"
    tushare_token: SecretStr | None = None
    timeout_seconds: int = Field(default=30, gt=0)
    retry_times: int = Field(default=3, ge=0)

    @field_validator("tushare_token", mode="before")
    @classmethod
    def empty_token_as_none(cls, value: Any) -> Any:
        if value == "":
            return None
        return value
