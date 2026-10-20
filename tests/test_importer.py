from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cs_deep_reader.errors import InvalidBookError
from cs_deep_reader.importer import BookImporter
from cs_deep_reader.models import ExtractionResult, PageResult, TocEntry
from cs_deep_reader.paths import LibraryPaths


class StubExtractor:
    def extract(self, source: Path) -> ExtractionResult:
        page = PageResult(1, "# PDF page 1\n\nSource text\n", "reliable-text")
        return ExtractionResult(1, (page,), (TocEntry(1, "Start", 1),))


class BookImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "book.pdf"
        self.source.write_bytes(b"%PDF test source")
        self.importer = BookImporter(LibraryPaths(self.root / "library"), StubExtractor())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_import_builds_knowledge_state_and_keeps_source_unchanged(self) -> None:
        before = self.source.read_bytes()
        manifest = self.importer.import_book(self.source, "Data Structures", None)
        book = self.root / "library/books/data-structures"
        self.assertEqual(before, self.source.read_bytes())
        self.assertTrue((book / "knowledge/algorithms.md").is_file())
        self.assertTrue((book / "progress.json").is_file())
        self.assertFalse(manifest["source_modified"])

    def test_duplicate_book_id_is_rejected_without_overwrite(self) -> None:
        self.importer.import_book(self.source, "Data Structures", None)
        with self.assertRaisesRegex(InvalidBookError, "already exists"):
            self.importer.import_book(self.source, "Data Structures", None)

    def test_non_pdf_input_is_rejected(self) -> None:
        text = self.root / "notes.txt"
        text.write_text("not a PDF", encoding="utf-8")
        with self.assertRaisesRegex(InvalidBookError, "Only PDF"):
            self.importer.import_book(text, None, None)

    def test_non_ascii_title_gets_stable_hash_slug(self) -> None:
        manifest = self.importer.import_book(self.source, "操作系统", None)
        self.assertRegex(manifest["book_id"], r"^book-[a-f0-9]{8}$")


if __name__ == "__main__":
    unittest.main()
