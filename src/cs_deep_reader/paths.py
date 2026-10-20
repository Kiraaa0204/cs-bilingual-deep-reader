"""Centralized, validated project paths."""

import re
from pathlib import Path

from .errors import InvalidBookError


BOOK_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class LibraryPaths:
    """Resolve paths without allowing traversal outside the library."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    @property
    def books(self) -> Path:
        return self.root / "books"

    def book(self, book_id: str) -> Path:
        self._validate_book_id(book_id)
        return self.books / book_id

    def require_book(self, book_id: str) -> Path:
        path = self.book(book_id)
        if not path.is_dir():
            raise InvalidBookError(f"Unknown book: {book_id}")
        return path

    @staticmethod
    def _validate_book_id(book_id: str) -> None:
        if not BOOK_ID_PATTERN.fullmatch(book_id):
            raise InvalidBookError(f"Invalid book id: {book_id}")
