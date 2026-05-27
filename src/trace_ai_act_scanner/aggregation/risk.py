"""Confidence-weighted risk score computation with context multipliers."""

from __future__ import annotations

import json
from typing import Any, Dict, Sequence

from trace_ai_act_scanner.models import Signal

_HIGH_RISK_KEYWORDS = (
    "employment", "recruitment", "education", "credit",
    "biometric", "law_enforcement", "police", "border",
)
_EU_KEYWORDS = ("eu_market", "european_union", "union", "spain", "canarias", "canary")
_ROLE_KEYWORDS = ("provider", "deployer", "controller", "processor")


def compute_risk_score(signals: Sequence[Signal], config: Dict[str, Any]) -> int:
    """Return a 0..100 integer risk score from confidence-weighted signals.

    The score is the sum of ``weight * confidence`` over all signals, scaled
    by context multipliers derived from the optional ``config`` (intended
    purpose, market, role).
    """
    raw = sum(s.weight * s.confidence for s in signals)
    multiplier = 1.0
    config_text = json.dumps(config, ensure_ascii=False).lower() if config else ""
    if any(k in config_text for k in _HIGH_RISK_KEYWORDS):
        multiplier += 0.12
    if any(k in config_text for k in _EU_KEYWORDS):
        multiplier += 0.05
    if any(k in config_text for k in _ROLE_KEYWORDS):
        multiplier += 0.05
    return min(100, int(round(raw * multiplier)))
