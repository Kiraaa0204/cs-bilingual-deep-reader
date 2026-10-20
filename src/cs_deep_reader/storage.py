"""Atomic JSON persistence."""

import json
import os
from pathlib import Path
from typing import Any


class JsonStore:
    """Read and atomically replace one JSON document."""

    def read(self, path: Path) -> dict[str, Any]:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)

    def write(self, path: Path, value: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        self._write_temporary(temporary, value)
        os.replace(temporary, path)

    @staticmethod
    def _write_temporary(path: Path, value: dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
