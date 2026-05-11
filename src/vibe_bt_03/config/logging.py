from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LoggingSettings(BaseModel):
    level: LogLevel = "INFO"
    to_file: bool = True
    file: str = "./logs/app.log"

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, value: str) -> str:
        return value.upper()
