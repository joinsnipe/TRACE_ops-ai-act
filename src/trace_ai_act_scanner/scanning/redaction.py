"""Secret redaction and content hashing for snippet protection."""

from __future__ import annotations

import hashlib
import re

_SECRET_PATTERNS = (
    r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]+['\"]",
    r"sk-[A-Za-z0-9_\-]{20,}",
    r"AKIA[0-9A-Z]{16}",
)


def file_hash(source: str) -> str:
    """Stable 16-char hex hash used when snippets are omitted from reports."""
    return hashlib.sha256(source.encode("utf-8", errors="ignore")).hexdigest()[:16]


def redact_secrets(text: str) -> str:
    """Replace common secret patterns with ``[REDACTED_SECRET]``."""
    if not text:
        return text
    out = text
    for pattern in _SECRET_PATTERNS:
        out = re.sub(pattern, "[REDACTED_SECRET]", out)
    return out
