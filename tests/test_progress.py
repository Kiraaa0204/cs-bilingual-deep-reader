from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cs_deep_reader.progress import ProgressService


class ProgressServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.path = Path(self.temporary.name) / "progress.json"
        self.service = ProgressService()
        self.service.create(self.path, "systems-book")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_create_and_update_position_round_trip(self) -> None:
        updated = self.service.set_position(self.path, 18, "2", "2.3")
        loaded = self.service.load(self.path)
        self.assertEqual(updated.position, loaded.position)
        self.assertEqual(18, loaded.position.page)

    def test_non_positive_page_is_rejected_without_change(self) -> None:
        before = self.path.read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "positive"):
            self.service.set_position(self.path, 0, "", "")
        self.assertEqual(before, self.path.read_text(encoding="utf-8"))

    def test_error_log_preserves_diagnostic_fields(self) -> None:
        error = {"concept": "Big-O", "question": "q", "answer": "a", "correction": "c"}
        result = self.service.add_error(self.path, error)
        self.assertEqual("Big-O", result.errors[0]["concept"])
        self.assertIn("recorded_at", result.errors[0])

    def test_due_selects_overdue_and_optionally_weak(self) -> None:
        with patch("cs_deep_reader.progress.date") as mocked_date:
            mocked_date.today.return_value = date(2026, 10, 20)
            self.service.assess(self.path, "tree", 2, 5, "partial")
            normal = self.service.due(self.path)
            weak = self.service.due(self.path, include_weak=True)
        self.assertEqual([], normal)
        self.assertEqual("tree", weak[0]["concept"])


if __name__ == "__main__":
    unittest.main()
