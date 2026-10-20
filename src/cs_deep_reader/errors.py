"""Domain exceptions presented cleanly by the CLI."""


class ReaderError(Exception):
    """Base error for expected user-facing failures."""


class InvalidBookError(ReaderError):
    """Raised when a book id or source is invalid."""


class ExtractionError(ReaderError):
    """Raised when a PDF cannot be safely extracted."""
