from datetime import date
import unittest

from cs_deep_reader.models import ReviewRecord
from cs_deep_reader.review import ReviewScheduler


class ReviewSchedulerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scheduler = ReviewScheduler()
        self.today = date(2026, 10, 20)

    def test_low_score_marks_concept_weak_and_reviews_tomorrow(self) -> None:
        record = self.scheduler.assess("heap", 2, None, self.today, 8, "confused invariant")
        self.assertEqual("weak", record.state)
        self.assertEqual("2026-10-21", record.next_review)
        self.assertEqual(0, record.repetitions)

    def test_transfer_score_marks_concept_mastered(self) -> None:
        record = self.scheduler.assess("heap", 4, None, self.today, 8, "applied to new input")
        self.assertEqual("mastered", record.state)
        self.assertEqual("2026-10-21", record.next_review)
        self.assertEqual(1, record.repetitions)

    def test_successive_success_extends_interval(self) -> None:
        previous = ReviewRecord("heap", 4, "mastered", 1, "2026-10-20")
        record = self.scheduler.assess("heap", 5, previous, self.today, 8, "derived complexity")
        self.assertEqual("2026-10-23", record.next_review)
        self.assertEqual(2, record.repetitions)

    def test_invalid_score_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "0 to 5"):
            self.scheduler.assess("heap", 6, None, self.today, None, "")


if __name__ == "__main__":
    unittest.main()
