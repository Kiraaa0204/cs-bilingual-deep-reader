from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cs_deep_reader.errors import InvalidBookError
from cs_deep_reader.paths import LibraryPaths


class LibraryPathsTests(unittest.TestCase):
    def test_valid_book_id_resolves_under_books(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = LibraryPaths(Path(temporary))
            self.assertEqual(paths.books / "operating-systems", paths.book("operating-systems"))

    def test_traversal_book_id_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = LibraryPaths(Path(temporary))
            with self.assertRaises(InvalidBookError):
                paths.book("../outside")

    def test_missing_book_is_reported(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = LibraryPaths(Path(temporary))
            with self.assertRaisesRegex(InvalidBookError, "Unknown book"):
                paths.require_book("missing")


if __name__ == "__main__":
    unittest.main()
