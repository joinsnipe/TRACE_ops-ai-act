"""TRACE AI Act Risk Scanner.

Open-source technical scanner for early EU AI Act and GDPR risk signals.

This package exposes the public API needed to embed the scanner in other tools.
The CLI lives in :mod:`trace_ai_act_scanner.cli`.

Public API
----------
- :func:`scan` — run the scanner programmatically over a path.
- :class:`ScanReport`, :class:`Signal`, :class:`ScanSummary` — result dataclasses.
- :data:`SCHEMA_VERSION` — current version of the public JSON output schema.

This tool identifies technical signals that may require legal, technical and
operational review. It is **not legal advice** and does **not** certify
compliance with Regulation (EU) 2024/1689 or GDPR.
"""

from __future__ import annotations

__version__ = "0.2.0"
SCHEMA_VERSION = "1.0"

from trace_ai_act_scanner.models import Rule, ScanReport, ScanSummary, Signal
from trace_ai_act_scanner.scanning.scanner import scan

__all__ = [
    "__version__",
    "SCHEMA_VERSION",
    "Rule",
    "Signal",
    "ScanSummary",
    "ScanReport",
    "scan",
]
