from __future__ import annotations

from dataclasses import dataclass, field

from vibe_bt_03.database.api.types import SaveResult


@dataclass(frozen=True)
class IngestionResult:
    """Summary returned by an ingestion workflow."""

    dataset: str
    source: str | None = None
    provider: str | None = None
    fetched: int = 0
    standardized: int = 0
    saved: SaveResult = field(default_factory=SaveResult)
    dry_run: bool = False
    warnings: tuple[str, ...] = ()
    ensured_instruments: int = 0

    @property
    def inserted(self) -> int:
        return self.saved.inserted

    @property
    def updated(self) -> int:
        return self.saved.updated

    @property
    def skipped(self) -> int:
        return self.saved.skipped

    @property
    def persisted(self) -> int:
        return self.inserted + self.updated

    def merge(self, other: IngestionResult) -> IngestionResult:
        if self.dataset != other.dataset:
            raise ValueError("cannot merge ingestion results from different datasets")
        if self.source != other.source:
            raise ValueError("cannot merge ingestion results from different sources")
        if self.provider != other.provider:
            raise ValueError("cannot merge ingestion results from different providers")
        if self.dry_run != other.dry_run:
            raise ValueError("cannot merge dry-run and persisted ingestion results")

        return IngestionResult(
            dataset=self.dataset,
            source=self.source,
            provider=self.provider,
            fetched=self.fetched + other.fetched,
            standardized=self.standardized + other.standardized,
            saved=self.saved.merge(other.saved),
            dry_run=self.dry_run,
            warnings=self.warnings + other.warnings,
            ensured_instruments=self.ensured_instruments + other.ensured_instruments,
        )
