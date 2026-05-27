"""Serialise a :class:`ScanReport` to a schema-v1 compliant dict.

The schema is published at ``schema/trace-report-v1.json`` and the version
constant lives in :mod:`trace_ai_act_scanner`. The wire format intentionally
carries a top-level ``schema_version`` so downstream consumers (notably the
proprietary SPE Audit Reporting layer) can validate and route appropriately.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from trace_ai_act_scanner import SCHEMA_VERSION
from trace_ai_act_scanner.models import ScanReport


def report_to_dict(report: ScanReport) -> Dict[str, Any]:
    """Return a JSON-serialisable dict tagged with the current schema version."""
    return {
        "schema_version": SCHEMA_VERSION,
        "summary": asdict(report.summary),
        "signals": [asdict(s) for s in report.signals],
        "controls": report.controls,
        "config": report.config,
        "disclaimer": report.disclaimer,
    }
