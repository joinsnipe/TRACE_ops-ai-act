"""End-to-end scanning pipeline.

This module is the entry point used by both the CLI and by programmatic
consumers via :func:`trace_ai_act_scanner.scan`.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from trace_ai_act_scanner.aggregation.readiness import compute_readiness
from trace_ai_act_scanner.aggregation.risk import compute_risk_score
from trace_ai_act_scanner.aggregation.viability import classify_viability
from trace_ai_act_scanner.extractors.python_ast import extract_python_items
from trace_ai_act_scanner.extractors.text import extract_text_items
from trace_ai_act_scanner.matching.matcher import match_rule
from trace_ai_act_scanner.matching.tokenizer import line_context
from trace_ai_act_scanner.models import Rule, ScanReport, ScanSummary, Signal
from trace_ai_act_scanner.rules import (
    load_builtin_rules,
    load_custom_rules,
    load_required_controls,
    merge_rules,
)
from trace_ai_act_scanner.scanning.ignore import filter_signals, load_ignores
from trace_ai_act_scanner.scanning.redaction import file_hash, redact_secrets
from trace_ai_act_scanner.scanning.walker import iter_files

log = logging.getLogger(__name__)

DISCLAIMER = (
    "This tool identifies technical and documentary signals that may require "
    "EU AI Act/GDPR review. It is not legal advice and does not determine compliance."
)


def _scan_file(
    path: Path,
    target_root: Path,
    rules: Sequence[Rule],
    no_snippets: bool,
) -> Tuple[List[Signal], Dict[str, List[Dict[str, Any]]]]:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        log.warning("Could not read %s: %s", path, exc)
        return [], {}

    rel = str(path.relative_to(target_root)) if target_root.is_dir() else str(path)
    items = (
        extract_python_items(source, str(path))
        if path.suffix.lower() == ".py"
        else extract_text_items(source)
    )

    signals: List[Signal] = []
    controls: Dict[str, List[Dict[str, Any]]] = {}
    seen: set = set()

    for symbol, line, node_type, context in items:
        for rule in rules:
            result = match_rule(rule, symbol, context)
            if not result:
                continue
            matched_text, conf = result
            dedupe_key = (rule.id, rel, line, matched_text.lower())
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            evidence_raw = line_context(source, line, radius=1) or context
            evidence = (
                f"[SNIPPET OMITTED: {file_hash(evidence_raw)}]"
                if no_snippets
                else redact_secrets(evidence_raw)
            )
            symbol_redacted = redact_secrets(symbol[:200])
            matched_redacted = redact_secrets(matched_text)

            if rule.bucket == "governance_control":
                controls.setdefault(rule.id, []).append(
                    {
                        "file": rel,
                        "line": line,
                        "matched": matched_redacted,
                        "node_type": node_type,
                        "evidence": evidence[:500] if not no_snippets else evidence,
                    }
                )
            else:
                signals.append(
                    Signal(
                        rule_id=rule.id,
                        bucket=rule.bucket,
                        legal_basis=rule.legal_basis,
                        label=rule.label,
                        severity=rule.severity,
                        weight=rule.weight,
                        file=rel,
                        line=line,
                        symbol=symbol_redacted,
                        matched=matched_redacted,
                        evidence=evidence[:700] if not no_snippets else evidence,
                        confidence=conf,
                        node_type=node_type,
                        guidance=rule.guidance,
                    )
                )
    return signals, controls


def scan(
    target: str,
    *,
    config: Optional[Dict[str, Any]] = None,
    no_snippets: bool = False,
    custom_rules_dir: Optional[Path] = None,
) -> ScanReport:
    """Run the scanner over ``target`` and return a :class:`ScanReport`."""
    config = config or {}
    target_path = Path(target).resolve()

    risk_rules, control_rules = load_builtin_rules()
    if custom_rules_dir is not None:
        c_risk, c_ctrl = load_custom_rules(custom_rules_dir)
        risk_rules = merge_rules(risk_rules, c_risk)
        control_rules = merge_rules(control_rules, c_ctrl)
    all_rules: List[Rule] = list(risk_rules) + list(control_rules)

    required_controls_by_bucket = load_required_controls()

    all_signals: List[Signal] = []
    controls: Dict[str, List[Dict[str, Any]]] = {}
    files_scanned = 0

    excludes = config.get("exclude", []) if isinstance(config, dict) else []
    for path in iter_files(target_path, excludes):
        files_scanned += 1
        root = target_path if target_path.is_dir() else path.parent
        file_signals, file_controls = _scan_file(path, root, all_rules, no_snippets)
        all_signals.extend(file_signals)
        for cid, hits in file_controls.items():
            controls.setdefault(cid, []).extend(hits)

    # Apply .traceignore filtering
    ignores = load_ignores(target_path)
    initial_signals_count = len(all_signals)
    silenced_signals = []
    if ignores:
        all_signals, silenced_signals = filter_signals(all_signals, ignores)
    ignored_count = len(silenced_signals)

    risk_score, coverage_confidence = compute_risk_score(all_signals, config)
    readiness_score, missing_controls = compute_readiness(
        all_signals, controls, required_controls_by_bucket
    )

    blockers = sum(
        1
        for s in all_signals
        if s.bucket == "article_5_prohibited_practice_signal" and s.confidence >= 0.55
    )
    high_risk = sum(
        1
        for s in all_signals
        if s.bucket == "annex_iii_high_risk_signal" and s.confidence >= 0.50
    )
    transparency = sum(
        1
        for s in all_signals
        if s.bucket == "article_50_transparency_signal" and s.confidence >= 0.50
    )
    gdpr = sum(
        1
        for s in all_signals
        if s.bucket == "gdpr_data_protection_overlap" and s.confidence >= 0.50
    )

    notes = [
        "This is a static signal scanner. Treat results as triage, not as a legal conclusion.",
        "A clean scan does not prove compliance; risky intent can exist outside code names.",
    ]
    if blockers:
        notes.append(
            "Article 5 signals deserve priority because prohibited-practice exposure "
            "can block deployment regardless of later controls."
        )
    if high_risk and missing_controls:
        notes.append(
            "High-risk signals require evidence of governance controls: risk management, "
            "data governance, documentation, logs, human oversight, robustness and monitoring."
        )
    if gdpr:
        notes.append(
            "GDPR overlap detected: AI Act review should be paired with "
            "privacy-by-design/DPIA analysis where personal data is involved."
        )
    if ignored_count > 0:
        notes.append(f"{ignored_count} signals were silenced via .traceignore exclusions.")

    control_count = sum(1 for cid, hits in controls.items() if hits)

    summary = ScanSummary(
        target=target_path.name,
        files_scanned=files_scanned,
        signals_total=len(all_signals),
        risk_score=risk_score,
        coverage_confidence=coverage_confidence,
        readiness_score=readiness_score,
        viability=classify_viability(risk_score, blockers, high_risk, len(missing_controls)),
        blockers=blockers,
        potential_high_risk=high_risk,
        transparency_risks=transparency,
        gdpr_overlaps=gdpr,
        governance_controls_detected=control_count,
        missing_governance_controls=missing_controls,
        notes=notes,
    )

    all_signals.sort(key=lambda s: (s.weight * s.confidence, s.confidence), reverse=True)

    return ScanReport(
        summary=summary,
        signals=all_signals,
        controls=controls,
        config=config,
        disclaimer=DISCLAIMER,
        silenced_signals=silenced_signals,
    )
