from __future__ import annotations

from typing import Any

from pydantic import BaseModel, SecretStr, field_validator


class DatabaseSettings(BaseModel):
    driver: str = "postgresql+psycopg"
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: SecretStr | None = None
    name: str = "vibe_bt"
    echo: bool = False

    @field_validator("password", mode="before")
    @classmethod
    def empty_password_as_none(cls, value: Any) -> Any:
        if value == "":
            return None
        return value

    @property
    def url(self) -> str:
        if self.password is None:
            credentials = self.user
        else:
            credentials = f"{self.user}:{self.password.get_secret_value()}"

        return f"{self.driver}://{credentials}@{self.host}:{self.port}/{self.name}"
