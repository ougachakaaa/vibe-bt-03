from __future__ import annotations


class IngestionError(RuntimeError):
    """Base error for data ingestion workflows."""


class IngestionValidationError(IngestionError):
    """Raised when incoming ingestion data cannot be standardized."""


class IngestionLookupError(IngestionError):
    """Raised when required reference data cannot be resolved."""
