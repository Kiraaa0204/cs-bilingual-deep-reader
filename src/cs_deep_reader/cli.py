"""Command-line interface used by the Codex Skill."""

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from .errors import ReaderError
from .importer import BookImporter
from .paths import LibraryPaths
from .progress import ProgressService
from .storage import JsonStore


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def library_paths() -> LibraryPaths:
    return LibraryPaths(project_root() / "library")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cs-deep-reader")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_import(subparsers)
    _add_book_queries(subparsers)
    _add_position(subparsers)
    _add_mastery(subparsers)
    _add_error(subparsers)
    _add_due(subparsers)
    return parser


def _add_import(subparsers: Any) -> None:
    command = subparsers.add_parser("import-book", help="extract a PDF into the local library")
    command.add_argument("source", type=Path)
    command.add_argument("--title")
    command.add_argument("--book-id")


def _add_book_queries(subparsers: Any) -> None:
    subparsers.add_parser("list-books", help="list imported textbooks")
    command = subparsers.add_parser("status", help="show saved reading status")
    command.add_argument("--book", required=True)


def _book_argument(command: Any) -> None:
    command.add_argument("--book", required=True)


def _add_position(subparsers: Any) -> None:
    command = subparsers.add_parser("set-position", help="save the last completed position")
    _book_argument(command)
    command.add_argument("--page", required=True, type=int)
    command.add_argument("--chapter", default="")
    command.add_argument("--section", default="")


def _add_mastery(subparsers: Any) -> None:
    command = subparsers.add_parser("record-mastery", help="record an evaluated learner answer")
    _book_argument(command)
    command.add_argument("--concept", required=True)
    command.add_argument("--score", required=True, type=int)
    command.add_argument("--source-page", type=int)
    command.add_argument("--evidence", default="")


def _add_error(subparsers: Any) -> None:
    command = subparsers.add_parser("log-error", help="record one misconception")
    _book_argument(command)
    for name in ("concept", "question", "answer", "correction"):
        command.add_argument(f"--{name}", required=True)
    command.add_argument("--source-page", type=int)


def _add_due(subparsers: Any) -> None:
    command = subparsers.add_parser("due", help="list due review concepts")
    _book_argument(command)
    command.add_argument("--include-weak", action="store_true")


def execute(arguments: argparse.Namespace) -> Any:
    paths = library_paths()
    if arguments.command == "import-book":
        return BookImporter(paths).import_book(arguments.source, arguments.title, arguments.book_id)
    if arguments.command == "list-books":
        return _list_books(paths)
    book_path = paths.require_book(arguments.book)
    return _execute_progress(arguments, book_path)


def _list_books(paths: LibraryPaths) -> list[dict[str, Any]]:
    manifests = sorted(paths.books.glob("*/manifest.json")) if paths.books.exists() else []
    return [JsonStore().read(path) for path in manifests]


def _execute_progress(arguments: argparse.Namespace, book_path: Path) -> Any:
    service = ProgressService()
    progress_path = book_path / "progress.json"
    if arguments.command == "status":
        return service.load(progress_path).to_dict()
    if arguments.command == "set-position":
        return service.set_position(progress_path, arguments.page, arguments.chapter, arguments.section).to_dict()
    if arguments.command == "record-mastery":
        return service.assess(progress_path, arguments.concept, arguments.score, arguments.source_page, arguments.evidence).to_dict()
    if arguments.command == "log-error":
        return service.add_error(progress_path, _error_payload(arguments)).to_dict()
    return service.due(progress_path, arguments.include_weak)


def _error_payload(arguments: argparse.Namespace) -> dict[str, Any]:
    return {"concept": arguments.concept, "question": arguments.question, "answer": arguments.answer,
            "correction": arguments.correction, "source_page": arguments.source_page, "resolved": False}


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = execute(build_parser().parse_args(argv))
    except (ReaderError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
