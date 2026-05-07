from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SaveResult:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0

    def merge(self, other: SaveResult) -> SaveResult:
        return SaveResult(
            inserted=self.inserted + other.inserted,
            updated=self.updated + other.updated,
            skipped=self.skipped + other.skipped,
        )
