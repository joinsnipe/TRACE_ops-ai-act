"""Identifier splitting and word extraction.

The goal is to avoid false positives such as ``Trace`` matching the exact
term ``race``. We split identifiers into safe tokens (snake_case,
kebab-case, camelCase) and also keep a normalised compound form so that
multi-word technical names like ``face_recognition`` can be matched as a
single unit.
"""

from __future__ import annotations

import re
from typing import List

TOKEN_SPLIT_RE = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]*")


def split_identifier(value: str) -> List[str]:
    """Split an identifier into safe tokens plus a normalised compound form.

    Examples
    --------
    >>> split_identifier("face_recognition")
    ['face', 'recognition', 'face_recognition']
    >>> split_identifier("scoreCandidateAuto")
    ['score', 'candidate', 'auto', 'scorecandidateauto']
    >>> split_identifier("TraceASTVisitor")
    ['trace', 'ast', 'visitor', 'traceastvisitor']
    """
    if not value:
        return []
    pieces: List[str] = []
    for part in re.split(r"[^A-Za-z0-9]+", value):
        if not part:
            continue
        sub = TOKEN_SPLIT_RE.findall(part)
        pieces.extend(s.lower() for s in (sub or [part]))
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    if normalized:
        pieces.append(normalized)
    return pieces


def line_context(text: str, line_no: int, radius: int = 1, max_chars: int = 700) -> str:
    """Return up to ``radius`` lines around ``line_no`` from ``text``."""
    lines = text.splitlines()
    idx = max(line_no - 1, 0)
    start = max(idx - radius, 0)
    end = min(idx + radius + 1, len(lines))
    return "\n".join(lines[start:end]).strip()[:max_chars]
