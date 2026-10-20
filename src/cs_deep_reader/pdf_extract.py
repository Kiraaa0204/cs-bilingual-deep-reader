"""Page-preserving PDF extraction with explicit reliability warnings."""

from contextlib import closing
from pathlib import Path
from typing import Any

from .errors import ExtractionError
from .models import ExtractionResult, PageResult, TocEntry


MONOSPACE_MARKERS = ("mono", "courier", "consolas", "menlo", "code")


class PdfExtractor:
    """Extract ordered text blocks without modifying the source PDF."""

    def __init__(self, fitz_module: Any | None = None) -> None:
        self.fitz = fitz_module or self._load_fitz()

    def extract(self, source: Path) -> ExtractionResult:
        try:
            document = self.fitz.open(source)
        except Exception as exc:
            raise ExtractionError(f"Cannot open PDF: {exc}") from exc
        with closing(document):
            self._reject_encrypted(document)
            self._reject_empty(document)
            pages = tuple(self._extract_page(page, number) for number, page in enumerate(document, 1))
            return ExtractionResult(len(document), pages, self._toc(document))

    def _extract_page(self, page: Any, number: int) -> PageResult:
        blocks = page.get_text("dict", sort=True).get("blocks", [])
        rendered = [self._render_block(block) for block in blocks if "lines" in block]
        text = "\n\n".join(value for value in rendered if value).strip()
        warnings = self._warnings(page, text)
        status = self._status(warnings)
        return PageResult(number, self._page_markdown(number, text, status, warnings), status, tuple(warnings))

    def _render_block(self, block: dict[str, Any]) -> str:
        lines = [self._line_text(line) for line in block.get("lines", [])]
        text = "\n".join(line for line in lines if line).strip()
        return f"```text\n{text}\n```" if text and self._is_code(block) else text

    @staticmethod
    def _line_text(line: dict[str, Any]) -> str:
        return "".join(span.get("text", "") for span in line.get("spans", [])).rstrip()

    @staticmethod
    def _is_code(block: dict[str, Any]) -> bool:
        spans = [span for line in block.get("lines", []) for span in line.get("spans", [])]
        fonts = [str(span.get("font", "")).lower() for span in spans]
        return bool(fonts) and sum(any(marker in font for marker in MONOSPACE_MARKERS) for font in fonts) >= len(fonts) / 2

    @staticmethod
    def _warnings(page: Any, text: str) -> list[str]:
        warnings: list[str] = []
        image_count = len(page.get_images(full=True))
        if len(text.strip()) < 40 and image_count:
            warnings.append("ocr-needed: image-heavy page has too little extractable text")
        elif not text.strip():
            warnings.append("unverified: page has no extractable text")
        if text and text.count("�") / len(text) > 0.005:
            warnings.append("unverified: extracted text contains replacement characters")
        if PdfExtractor._may_have_layout_loss(page):
            warnings.append("layout-loss: drawings or multiple columns may affect tables/formulas/order")
        return warnings

    @staticmethod
    def _may_have_layout_loss(page: Any) -> bool:
        drawings = page.get_drawings() if hasattr(page, "get_drawings") else []
        return len(drawings) >= 8

    @staticmethod
    def _status(warnings: list[str]) -> str:
        if any(item.startswith("ocr-needed") for item in warnings):
            return "ocr-needed"
        if any(item.startswith("unverified") for item in warnings):
            return "unverified"
        return "layout-loss" if warnings else "reliable-text"

    @staticmethod
    def _page_markdown(number: int, text: str, status: str, warnings: list[str]) -> str:
        warning_lines = "\n".join(f"> WARNING: {warning}" for warning in warnings)
        notice = f"\n{warning_lines}\n" if warning_lines else "\n"
        body = text or "[No extractable text. Do not infer page content.]"
        return f"# PDF page {number}\n\n> Extraction status: {status}{notice}\n{body}\n"

    @staticmethod
    def _toc(document: Any) -> tuple[TocEntry, ...]:
        raw_entries = document.get_toc(simple=True) or []
        return tuple(TocEntry(int(level), str(title).strip(), int(page)) for level, title, page in raw_entries if int(page) > 0)

    @staticmethod
    def _reject_encrypted(document: Any) -> None:
        if getattr(document, "needs_pass", False):
            raise ExtractionError("Encrypted PDF requires a password; no content was extracted")

    @staticmethod
    def _reject_empty(document: Any) -> None:
        if len(document) == 0:
            raise ExtractionError("PDF has no pages")

    @staticmethod
    def _load_fitz() -> Any:
        try:
            import fitz
        except ImportError as exc:
            raise ExtractionError("PyMuPDF is missing. Install the project dependencies first.") from exc
        return fitz
