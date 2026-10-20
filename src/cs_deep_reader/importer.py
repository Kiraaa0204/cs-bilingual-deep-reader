"""Book import orchestration and knowledge-base scaffolding."""

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import InvalidBookError
from .models import ExtractionResult
from .paths import LibraryPaths
from .pdf_extract import PdfExtractor
from .progress import ProgressService
from .storage import JsonStore


KNOWLEDGE_FILES = {
    "00-map.md": "# Knowledge Map\n\n## Chapters\n\n## Concept dependencies\n",
    "glossary.md": "# Glossary\n\n| 中文术语 | English term | Definition | Source |\n|---|---|---|---|\n",
    "formulas.md": "# Formulas\n\nRecord assumptions, derivations, units, and edge cases.\n",
    "algorithms.md": "# Algorithms\n\nRecord goals, invariants, correctness, complexity, and trade-offs.\n",
    "code-patterns.md": "# Code Patterns\n\nRecord execution traces and use/avoid guidance.\n",
    "pitfalls.md": "# Pitfalls\n\nRecord misconceptions, counterexamples, and diagnostic questions.\n",
}


class BookImporter:
    """Validate a PDF and create an isolated derived book workspace."""

    def __init__(self, paths: LibraryPaths, extractor: PdfExtractor | None = None) -> None:
        self.paths = paths
        self.extractor = extractor or PdfExtractor()
        self.store = JsonStore()

    def import_book(self, source: Path, title: str | None, book_id: str | None) -> dict[str, Any]:
        source = self._validate_source(source)
        digest = self._checksum(source)
        resolved_title = title or source.stem
        resolved_id = book_id or self._slug(resolved_title, digest)
        destination = self.paths.book(resolved_id)
        self._ensure_new(destination)
        extraction = self.extractor.extract(source)
        self._write_book(destination, source, resolved_title, resolved_id, digest, extraction)
        return self.store.read(destination / "manifest.json")

    def _write_book(self, destination: Path, source: Path, title: str, book_id: str, digest: str, extraction: ExtractionResult) -> None:
        (destination / "pages").mkdir(parents=True)
        (destination / "sessions").mkdir()
        self._write_pages(destination, extraction)
        self._write_structure(destination, extraction)
        self._write_knowledge(destination)
        self.store.write(destination / "manifest.json", self._manifest(source, title, book_id, digest, extraction))
        ProgressService(self.store).create(destination / "progress.json", book_id)

    @staticmethod
    def _write_pages(destination: Path, extraction: ExtractionResult) -> None:
        for page in extraction.pages:
            (destination / "pages" / f"page-{page.number:04d}.md").write_text(page.markdown, encoding="utf-8")

    @staticmethod
    def _write_structure(destination: Path, extraction: ExtractionResult) -> None:
        header = "# Book Structure\n\n"
        if extraction.toc:
            lines = [f"{'  ' * (item.level - 1)}- p.{item.page}: {item.title}" for item in extraction.toc]
        else:
            lines = [f"- p.{number}: [No PDF outline entry]" for number in range(1, extraction.page_count + 1)]
        (destination / "structure.md").write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _write_knowledge(destination: Path) -> None:
        knowledge = destination / "knowledge"
        knowledge.mkdir()
        for name, content in KNOWLEDGE_FILES.items():
            (knowledge / name).write_text(content, encoding="utf-8")

    @staticmethod
    def _manifest(source: Path, title: str, book_id: str, digest: str, extraction: ExtractionResult) -> dict[str, Any]:
        warnings = {str(page.number): list(page.warnings) for page in extraction.pages if page.warnings}
        return {"schema_version": 1, "book_id": book_id, "title": title, "source_path": str(source), "source_sha256": digest,
                "page_count": extraction.page_count, "imported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "warning_pages": warnings, "source_modified": False}

    @staticmethod
    def _validate_source(source: Path) -> Path:
        resolved = source.expanduser().resolve()
        if not resolved.is_file():
            raise InvalidBookError(f"PDF not found: {resolved}")
        if resolved.suffix.lower() != ".pdf":
            raise InvalidBookError("Only PDF textbooks are supported")
        return resolved

    @staticmethod
    def _checksum(source: Path) -> str:
        digest = hashlib.sha256()
        with source.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _slug(title: str, digest: str) -> str:
        ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
        return slug[:48].strip("-") or f"book-{digest[:8]}"

    @staticmethod
    def _ensure_new(destination: Path) -> None:
        if destination.exists():
            raise InvalidBookError(f"Book already exists: {destination.name}")
