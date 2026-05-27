"""Human-readable Markdown report renderer."""

from __future__ import annotations

from typing import Dict, List

from trace_ai_act_scanner.models import Rule, ScanReport
from trace_ai_act_scanner.rules import load_builtin_rules


def _control_lookup() -> Dict[str, Rule]:
    _, controls = load_builtin_rules()
    return {r.id: r for r in controls}


def render_markdown(report: ScanReport, max_signals: int = 30) -> str:
    """Render a Markdown report. Showing only top ``max_signals`` signals."""
    s = report.summary
    lines: List[str] = [
        "# TRACE AI Act Risk Scanner — Report",
        "",
        f"**Target:** `{s.target}`",
        f"**Files scanned:** {s.files_scanned}",
        f"**Signals found:** {s.signals_total}",
        f"**Risk score:** {s.risk_score}/100",
        f"**Governance readiness:** {s.readiness_score}/100",
        f"**Viability:** `{s.viability}`",
        "",
        "## Signal summary",
        "",
        f"- Article 5 blocker signals: {s.blockers}",
        f"- Annex III high-risk signals: {s.potential_high_risk}",
        f"- Article 50 transparency signals: {s.transparency_risks}",
        f"- GDPR/data-protection overlaps: {s.gdpr_overlaps}",
        f"- Governance controls detected: {s.governance_controls_detected}",
        "",
    ]

    controls = _control_lookup()
    if s.missing_governance_controls:
        lines += ["## Missing governance controls", ""]
        for cid in s.missing_governance_controls:
            ctrl = controls.get(cid)
            label = ctrl.label if ctrl else cid
            basis = ctrl.legal_basis if ctrl else ""
            lines.append(f"- `{cid}` — {label} ({basis})")
        lines.append("")

    lines += ["## Top signals", ""]
    for sig in report.signals[:max_signals]:
        lines += [
            f"### {sig.severity}: {sig.label}",
            f"- Rule: `{sig.rule_id}`",
            f"- Legal basis: {sig.legal_basis}",
            f"- Location: `{sig.file}:{sig.line}`",
            f"- Matched: `{sig.matched}` | Confidence: {sig.confidence}",
            f"- Guidance: {sig.guidance}",
            "",
            "```",
            sig.evidence,
            "```",
            "",
        ]

    if report.controls:
        lines += ["## Detected governance controls", ""]
        for cid, hits in sorted(report.controls.items()):
            ctrl = controls.get(cid)
            label = ctrl.label if ctrl else cid
            lines.append(f"- `{cid}` — {label}: {len(hits)} hit(s)")
        lines.append("")

    lines += ["## Notes", ""]
    for note in s.notes:
        lines.append(f"- {note}")
    lines += ["", f"> {report.disclaimer}", ""]

    return "\n".join(lines)
