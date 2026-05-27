"""Discover scannable files under a target path."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Sequence

SUPPORTED_EXTENSIONS = frozenset(
    {
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".json", ".yaml", ".yml", ".toml",
        ".md", ".txt", ".html", ".css",
    }
)

DEFAULT_EXCLUDES = frozenset(
    {
        ".git", ".venv", "venv", "node_modules", "dist", "build",
        "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    }
)


def iter_files(target: Path, excludes: Sequence[str] = ()) -> Iterable[Path]:
    """Yield paths under ``target`` with supported extensions, honouring excludes."""
    excludes_set = set(excludes) | DEFAULT_EXCLUDES
    if target.is_file():
        if target.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield target
        return
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in excludes_set and not d.startswith(".")]
        for filename in files:
            path = Path(root) / filename
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield path
