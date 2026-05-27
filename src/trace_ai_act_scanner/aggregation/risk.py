"""Confidence-weighted risk score computation with context multipliers."""

from __future__ import annotations

import json
from typing import Any, Dict, Sequence, Tuple

from trace_ai_act_scanner.models import Signal

_HIGH_RISK_KEYWORDS = (
    "employment", "recruitment", "education", "credit",
    "biometric", "law_enforcement", "police", "border",
)
_EU_KEYWORDS = ("eu_market", "european_union", "union", "spain", "canarias", "canary")
_ROLE_KEYWORDS = ("provider", "deployer", "controller", "processor")


def compute_risk_score(signals: Sequence[Signal], config: Dict[str, Any]) -> Tuple[int, float]:
    """Return a (risk_score, coverage_confidence) tuple.

    The score is capped based on the maximum severity found, adding a decaying factor
    for additional signals, rather than a raw unbounded sum.
    """
    if not signals:
        return 0, 1.0

    coverage_confidence = sum(s.confidence for s in signals) / len(signals)
    
    max_weight = max(s.weight for s in signals)
    raw_additional = sum(s.weight * s.confidence for s in signals) / 10.0
    
    raw = max_weight + raw_additional

    multiplier = 1.0
    config_text = json.dumps(config, ensure_ascii=False).lower() if config else ""
    if any(k in config_text for k in _HIGH_RISK_KEYWORDS):
        multiplier += 0.12
    if any(k in config_text for k in _EU_KEYWORDS):
        multiplier += 0.05
    if any(k in config_text for k in _ROLE_KEYWORDS):
        multiplier += 0.05
        
    return min(100, int(round(raw * multiplier))), round(coverage_confidence, 2)
