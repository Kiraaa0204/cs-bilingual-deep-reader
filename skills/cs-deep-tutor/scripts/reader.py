#!/usr/bin/env python3
"""Project-local entry point for the CS deep-reading CLI."""

from pathlib import Path
import sys


def add_source_root() -> None:
    project_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project_root / "src"))


if __name__ == "__main__":
    add_source_root()
    from cs_deep_reader.cli import main

    raise SystemExit(main())
