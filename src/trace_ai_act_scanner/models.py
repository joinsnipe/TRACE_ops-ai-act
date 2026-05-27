"""Core dataclasses used across the scanner.

These are intentionally framework-free so they can be serialised to JSON or
consumed by downstream tools (e.g. the proprietary SPE Audit Reporting layer)
without coupling to any extractor or matcher implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class Rule:
    """A rule fed into the matcher.

    Rules are normally loaded from YAML under ``rules/builtin/`` rather than
    constructed by hand. See :mod:`trace_ai_act_scanner.rules.loader`.

    Notes
    -----
    The ``contradicts_public_claims`` field is **opt-in metadata** consumed by
    the proprietary SPE Audit Reporting layer to perform narrative-vs-code
    alignment analysis. The open-source scanner ignores it. It is exposed here
    so rule authors can document which public claims a signal typically
    contradicts.
    """

    id: str
    bucket: str
    legal_basis: str
    label: str
    severity: str
    weight: int
    exact_terms: Tuple[str, ...] = ()
    phrases: Tuple[str, ...] = ()
    regexes: Tuple[str, ...] = ()
    context_terms: Tuple[str, ...] = ()
    required_context: Tuple[str, ...] = ()
    negative_terms: Tuple[str, ...] = ()
    term_exclusions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    guidance: str = ""
    contradicts_public_claims: Tuple[str, ...] = ()


@dataclass
class Signal:
    """A single signal raised by the scanner against a file."""

    rule_id: str
    bucket: str
    legal_basis: str
    label: str
    severity: str
    weight: int
    file: str
    line: int
    symbol: str
    matched: str
    evidence: str
    confidence: float
    node_type: str = "text"
    guidance: str = ""


@dataclass
class ScanSummary:
    """Aggregated scan-level metrics."""

    target: str
    files_scanned: int
    signals_total: int
    risk_score: int
    coverage_confidence: float
    readiness_state: str
    applicability: Dict[str, str]
    silenced_summary: Dict[str, Any]
    viability: str
    blockers: int
    potential_high_risk: int
    transparency_risks: int
    gdpr_overlaps: int
    governance_controls_detected: int
    missing_governance_controls: List[str]
    no_ignore_used: bool = False
    notes: List[str] = field(default_factory=list)


@dataclass
class ScanReport:
    """Top-level scan output.

    This object maps 1:1 to the JSON described by
    ``schema/trace-report-v1.json``. The ``schema_version`` is added by the
    JSON serialiser, not stored here, to keep the in-memory model decoupled
    from wire format.
    """

    summary: ScanSummary
    signals: List[Signal]
    controls: Dict[str, List[Dict[str, Any]]]
    config: Dict[str, Any]
    disclaimer: str
    silenced_signals: List[Dict[str, Any]] = field(default_factory=list)
