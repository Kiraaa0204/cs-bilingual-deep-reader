from pathlib import Path
import unittest

from cs_deep_reader.errors import ExtractionError
from cs_deep_reader.pdf_extract import PdfExtractor


def text_block(text: str, font: str = "Times") -> dict:
    return {"lines": [{"spans": [{"text": text, "font": font}]}]}


class FakePage:
    def __init__(self, blocks: list[dict], images: int = 0, drawings: int = 0) -> None:
        self.blocks = blocks
        self.images = images
        self.drawings = drawings

    def get_text(self, kind: str, sort: bool = False) -> dict:
        return {"blocks": self.blocks}

    def get_images(self, full: bool = False) -> list[object]:
        return [object()] * self.images

    def get_drawings(self) -> list[object]:
        return [object()] * self.drawings


class FakeDocument(list):
    needs_pass = False

    def get_toc(self, simple: bool = True) -> list[list[object]]:
        return [[1, "Foundations", 1]]

    def close(self) -> None:
        self.closed = True


class FakeFitz:
    def __init__(self, document: FakeDocument) -> None:
        self.document = document

    def open(self, source: Path) -> FakeDocument:
        return self.document


class PdfExtractorTests(unittest.TestCase):
    def test_extract_preserves_page_number_toc_and_code(self) -> None:
        page = FakePage([text_block("for item in data:", "Courier")])
        result = PdfExtractor(FakeFitz(FakeDocument([page]))).extract(Path("book.pdf"))
        self.assertEqual(1, result.page_count)
        self.assertIn("```text", result.pages[0].markdown)
        self.assertEqual("Foundations", result.toc[0].title)

    def test_image_only_page_is_marked_for_ocr(self) -> None:
        page = FakePage([], images=2)
        result = PdfExtractor(FakeFitz(FakeDocument([page]))).extract(Path("scan.pdf"))
        self.assertEqual("ocr-needed", result.pages[0].status)
        self.assertIn("Do not infer", result.pages[0].markdown)

    def test_complex_drawing_page_warns_about_layout(self) -> None:
        page = FakePage([text_block("a" * 80)], drawings=8)
        result = PdfExtractor(FakeFitz(FakeDocument([page]))).extract(Path("table.pdf"))
        self.assertEqual("layout-loss", result.pages[0].status)

    def test_blank_page_is_unverified_instead_of_reliable(self) -> None:
        result = PdfExtractor(FakeFitz(FakeDocument([FakePage([])]))).extract(Path("blank.pdf"))
        self.assertEqual("unverified", result.pages[0].status)

    def test_encrypted_document_is_rejected(self) -> None:
        document = FakeDocument([])
        document.needs_pass = True
        with self.assertRaisesRegex(ExtractionError, "password"):
            PdfExtractor(FakeFitz(document)).extract(Path("secret.pdf"))

    def test_zero_page_document_is_rejected(self) -> None:
        with self.assertRaisesRegex(ExtractionError, "no pages"):
            PdfExtractor(FakeFitz(FakeDocument([]))).extract(Path("empty.pdf"))


if __name__ == "__main__":
    unittest.main()
