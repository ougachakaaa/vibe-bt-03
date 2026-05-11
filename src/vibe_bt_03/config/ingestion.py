from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class IngestionSettings(BaseModel):
    stock_bar_start_date: date = date(2010, 1, 1)
    stock_bar_batch_size: int = Field(default=500, gt=0)
    retry_times: int = Field(default=3, ge=0)
    dry_run: bool = False
