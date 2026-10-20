"""Learning progress application service."""

from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .models import LearningProgress, Position
from .review import ReviewScheduler
from .storage import JsonStore


class ProgressService:
    """Validate and persist positions, mastery, errors, and due reviews."""

    def __init__(self, store: JsonStore | None = None) -> None:
        self.store = store or JsonStore()
        self.scheduler = ReviewScheduler()

    def create(self, path: Path, book_id: str) -> LearningProgress:
        progress = LearningProgress(book_id, updated_at=self._timestamp())
        self._save(path, progress)
        return progress

    def load(self, path: Path) -> LearningProgress:
        return LearningProgress.from_dict(self.store.read(path))

    def set_position(self, path: Path, page: int, chapter: str, section: str) -> LearningProgress:
        if page < 1:
            raise ValueError("page must be positive")
        progress = self.load(path)
        progress.position = Position(page, chapter, section)
        self._save(path, progress)
        return progress

    def assess(self, path: Path, concept: str, score: int, source_page: int | None, evidence: str) -> LearningProgress:
        progress = self.load(path)
        previous = progress.concepts.get(concept)
        progress.concepts[concept] = self.scheduler.assess(concept, score, previous, date.today(), source_page, evidence)
        self._save(path, progress)
        return progress

    def add_error(self, path: Path, error: dict[str, Any]) -> LearningProgress:
        progress = self.load(path)
        progress.errors.append({**error, "recorded_at": self._timestamp()})
        self._save(path, progress)
        return progress

    def due(self, path: Path, include_weak: bool = False) -> list[dict[str, Any]]:
        progress = self.load(path)
        today = date.today().isoformat()
        records = progress.concepts.values()
        selected = [record for record in records if record.next_review <= today or include_weak and record.state == "weak"]
        return [record.__dict__ for record in sorted(selected, key=lambda item: item.next_review)]

    def _save(self, path: Path, progress: LearningProgress) -> None:
        progress.updated_at = self._timestamp()
        self.store.write(path, progress.to_dict())

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
