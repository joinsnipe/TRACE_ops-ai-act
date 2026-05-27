"""SARIF 2.1.0 report renderer.

SARIF is the standard format consumed by GitHub Code Scanning, GitLab,
SonarQube and most modern security platforms. Emitting it lets users
publish TRACE results to their existing security dashboards.

Spec: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
"""

from __future__ import annotations

from typing import Any, Dict, List

from trace_ai_act_scanner import __version__
from trace_ai_act_scanner.models import ScanReport, Signal


_SEVERITY_TO_SARIF = {
    "ARTICLE_5_REVIEW_REQUIRED": "error",
    "HIGH_RISK_REVIEW": "warning",
    "TRANSPARENCY_REVIEW": "warning",
    "DATA_PROTECTION_REVIEW": "warning",
}


def _signal_to_result(sig: Signal) -> Dict[str, Any]:
    return {
        "ruleId": sig.rule_id,
        "level": _SEVERITY_TO_SARIF.get(sig.severity, "note"),
        "message": {"text": f"{sig.label}. {sig.guidance}".strip()},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": sig.file},
                    "region": {"startLine": max(1, sig.line)},
                }
            }
        ],
        "properties": {
            "confidence": sig.confidence,
            "weight": sig.weight,
            "bucket": sig.bucket,
            "legal_basis": sig.legal_basis,
            "matched": sig.matched,
        },
    }


def render_sarif(report: ScanReport) -> Dict[str, Any]:
    """Return a SARIF 2.1.0 document for ``report``."""
    rule_ids: List[str] = []
    seen_rules: set = set()
    rules: List[Dict[str, Any]] = []
    for sig in report.signals:
        if sig.rule_id in seen_rules:
            continue
        seen_rules.add(sig.rule_id)
        rule_ids.append(sig.rule_id)
        rules.append(
            {
                "id": sig.rule_id,
                "name": sig.rule_id,
                "shortDescription": {"text": sig.label},
                "fullDescription": {"text": sig.guidance or sig.label},
                "helpUri": "https://github.com/joinsnipe/TRACE_ops-ai-act",
                "properties": {"legal_basis": sig.legal_basis, "bucket": sig.bucket},
            }
        )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "TRACE AI Act Risk Scanner",
                        "version": __version__,
                        "informationUri": "https://github.com/joinsnipe/TRACE_ops-ai-act",
                        "rules": rules,
                    }
                },
                "results": [_signal_to_result(s) for s in report.signals],
                "properties": {
                    "risk_score": report.summary.risk_score,
                    "readiness_score": report.summary.readiness_score,
                    "viability": report.summary.viability,
                },
            }
        ],
    }
