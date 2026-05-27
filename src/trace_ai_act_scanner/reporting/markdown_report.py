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
        f"**Coverage confidence:** {s.coverage_confidence}",
        f"**Static governance readiness:** `{s.readiness_state}`",
        (
            "> *Note: Readiness state only applies when the scanner detects signals that require governance controls. A state of OUT_OF_SCOPE means no risk signals were found, so no specific AI Act controls are triggered by this scan. This does not constitute legal compliance advice.*"
            if s.readiness_state != "REVIEWED_NO_ACTION"
            else "> *Note: Signals were found but were manually reviewed and silenced via .traceignore (considered not applicable or false positives). Audit trail available.*"
        ),
        f"**Applicability:** {s.applicability.get('status', 'UNKNOWN')}",
        f"  - {s.applicability.get('message', '')}",
        f"**Viability:** `{s.viability}`",
    ]
    if s.no_ignore_used:
        lines.insert(2, "**Raw scan (--no-ignore):** `True`")
        
    lines += [
        "",
        "## Signal summary",
        "",
        f"- Article 5 blocker signals: {s.blockers}",
        f"- Annex III high-risk signals: {s.potential_high_risk}",
        f"- Article 50 transparency signals: {s.transparency_risks}",
        f"- GDPR/data-protection overlaps: {s.gdpr_overlaps}",
        f"- Governance controls detected: {s.governance_controls_detected}",
        "",
        "### Severity Breakdown",
        "| Severity | Count |",
        "| -------- | ----- |",
    ]
    
    severity_counts = {}
    for sig in report.signals:
        severity_counts[sig.severity] = severity_counts.get(sig.severity, 0) + 1
        
    for sev in sorted(severity_counts.keys()):
        lines.append(f"| {sev} | {severity_counts[sev]} |")
    lines.append("")

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
    
    # Group signals by severity
    by_severity = {}
    for sig in report.signals[:max_signals]:
        by_severity.setdefault(sig.severity, []).append(sig)
        
    for sev, sigs in by_severity.items():
        lines += [f"### {sev}", ""]
        for sig in sigs:
            lines += [
                f"#### {sig.label}",
                f"- Rule: `{sig.rule_id}`",
                f"- Legal basis: {sig.legal_basis}",
                f"- Location: [{sig.file}:{sig.line}](./{sig.file}#L{sig.line})",
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
        
    if s.silenced_summary and s.silenced_summary.get("total_silenced", 0) > 0:
        lines += [
            "",
            "## Silenced Summary",
            "",
            f"**Total silenced:** {s.silenced_summary.get('total_silenced')}",
            f"**Note:** {s.silenced_summary.get('note')}",
            "",
            "### By Rule",
        ]
        for rule, count in s.silenced_summary.get("by_rule", {}).items():
            lines.append(f"- `{rule}`: {count}")
            
    if report.silenced_signals:
        lines += ["", "## Silenced Signals (Audit Trail)", ""]
        for sil in report.silenced_signals:
            rule_id = sil.get("rule_id", "Unknown")
            file_loc = sil.get("file", "Unknown")
            line = sil.get("line", "?")
            reason = sil.get("reason", "No reason provided")
            lines.append(f"- **{rule_id}** at `{file_loc}:{line}`")
            lines.append(f"  - *Reason:* {reason}")
            
    lines += ["", f"> {report.disclaimer}", ""]

    return "\n".join(lines)
