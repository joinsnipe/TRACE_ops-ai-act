"""Common interface for file extractors.

An extractor reads a source file and emits ``(symbol, line, node_type, context)``
tuples that the matcher can consume.
"""

from __future__ import annotations

from typing import List, Protocol, Tuple

#: Each item is ``(symbol, line_number, node_type, surrounding_context)``.
ExtractedItem = Tuple[str, int, str, str]


class Extractor(Protocol):
    """Protocol implemented by all extractors."""

    def extract(self, source: str) -> List[ExtractedItem]:  # pragma: no cover
        ...
