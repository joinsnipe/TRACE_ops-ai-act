"""Tests for risk score aggregation."""

from trace_ai_act_scanner.aggregation.risk import compute_risk_score
from trace_ai_act_scanner.models import Signal


def _mk(weight: int, confidence: float, bucket: str = "annex_iii_high_risk_signal") -> Signal:
    return Signal(
        rule_id="X",
        bucket=bucket,
        legal_basis="",
        label="",
        severity="HIGH_RISK_REVIEW",
        weight=weight,
        file="f.py",
        line=1,
        symbol="",
        matched="",
        evidence="",
        confidence=confidence,
    )


def test_zero_when_no_signals():
    assert compute_risk_score([], {}) == 0


def test_capped_at_100():
    signals = [_mk(40, 0.9) for _ in range(10)]
    assert compute_risk_score(signals, {}) == 100


def test_multiplier_applied():
    s = [_mk(30, 0.5)]
    base = compute_risk_score(s, {})
    boosted = compute_risk_score(s, {"intended_purpose": "employment screening"})
    assert boosted > base
