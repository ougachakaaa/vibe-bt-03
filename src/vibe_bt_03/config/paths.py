from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class PathSettings(BaseModel):
    data_dir: Path = Path("./data")
    log_dir: Path = Path("./logs")
    cache_dir: Path = Path("./cache")
