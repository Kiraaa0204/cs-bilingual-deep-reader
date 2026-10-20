"""Mastery evaluation and spaced-review scheduling."""

from datetime import date, timedelta

from .models import ReviewRecord


INTERVAL_DAYS = (1, 3, 7, 14, 30, 60)


class ReviewScheduler:
    """Create the next review record from assessed evidence."""

    def assess(
        self, concept: str, score: int, previous: ReviewRecord | None,
        today: date, source_page: int | None, evidence: str,
    ) -> ReviewRecord:
        self._validate_score(score)
        repetitions = self._repetitions(score, previous)
        due = today + timedelta(days=self._interval(score, repetitions))
        return ReviewRecord(concept, score, self._state(score), repetitions, due.isoformat(), source_page, evidence)

    @staticmethod
    def _validate_score(score: int) -> None:
        if score not in range(6):
            raise ValueError("score must be from 0 to 5")

    @staticmethod
    def _repetitions(score: int, previous: ReviewRecord | None) -> int:
        return (previous.repetitions + 1) if score >= 3 and previous else int(score >= 3)

    @staticmethod
    def _interval(score: int, repetitions: int) -> int:
        if score < 3:
            return 1
        return INTERVAL_DAYS[min(repetitions - 1, len(INTERVAL_DAYS) - 1)]

    @staticmethod
    def _state(score: int) -> str:
        if score < 3:
            return "weak"
        return "mastered" if score >= 4 else "learning"
