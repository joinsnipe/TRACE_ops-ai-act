"""Generic text extractor used for non-Python files and as a fallback."""

from __future__ import annotations

from typing import List

from trace_ai_act_scanner.extractors.base import ExtractedItem
from trace_ai_act_scanner.matching.tokenizer import WORD_RE


def extract_text_items(source: str) -> List[ExtractedItem]:
    """Extract words and full lines from ``source`` for keyword/phrase matching."""
    items: List[ExtractedItem] = []
    for i, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        items.append((stripped[:300], i, "Line", stripped[:700]))
        for word in WORD_RE.findall(line):
            if len(word) >= 3:
                items.append((word, i, "Word", stripped[:700]))
    return items
