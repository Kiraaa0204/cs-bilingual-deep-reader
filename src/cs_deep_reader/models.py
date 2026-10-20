"""Serializable domain values for books and learning state."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class TocEntry:
    level: int
    title: str
    page: int


@dataclass(frozen=True)
class PageResult:
    number: int
    markdown: str
    status: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExtractionResult:
    page_count: int
    pages: tuple[PageResult, ...]
    toc: tuple[TocEntry, ...]


@dataclass
class Position:
    page: int = 1
    chapter: str = ""
    section: str = ""


@dataclass
class ReviewRecord:
    concept: str
    score: int
    state: str
    repetitions: int
    next_review: str
    source_page: int | None = None
    evidence: str = ""


@dataclass
class LearningProgress:
    book_id: str
    position: Position = field(default_factory=Position)
    concepts: dict[str, ReviewRecord] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearningProgress":
        position = Position(**data.get("position", {}))
        concepts = cls._records(data.get("concepts", {}))
        return cls(data["book_id"], position, concepts, data.get("errors", []), data.get("updated_at", ""))

    @staticmethod
    def _records(items: dict[str, Any]) -> dict[str, ReviewRecord]:
        return {name: ReviewRecord(**value) for name, value in items.items()}
