class DatabaseError(Exception):
    """Base exception for database boundary failures."""


class DatabaseNotConfiguredError(DatabaseError):
    """Raised when database access is attempted before configuration."""


class DatabaseValidationError(DatabaseError, ValueError):
    """Raised when data does not satisfy the database API contract."""


class DatabaseLookupError(DatabaseError, LookupError):
    """Raised when a required database entity cannot be found."""
