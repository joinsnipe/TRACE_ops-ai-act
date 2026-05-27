"""End-to-end scanning pipeline."""

from trace_ai_act_scanner.scanning.redaction import file_hash, redact_secrets
from trace_ai_act_scanner.scanning.scanner import DISCLAIMER, scan
from trace_ai_act_scanner.scanning.walker import (
    DEFAULT_EXCLUDES,
    SUPPORTED_EXTENSIONS,
    iter_files,
)

__all__ = [
    "scan",
    "DISCLAIMER",
    "iter_files",
    "SUPPORTED_EXTENSIONS",
    "DEFAULT_EXCLUDES",
    "redact_secrets",
    "file_hash",
]
