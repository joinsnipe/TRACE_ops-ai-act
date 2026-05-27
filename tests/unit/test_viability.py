"""Tests for viability classification."""

from trace_ai_act_scanner.aggregation.viability import classify_viability


def test_blocked_when_blocker_and_high_risk():
    assert classify_viability(80, blockers=1, high_risk=0, missing_controls=0) == \
        "BLOCKED_UNTIL_LEGAL_AND_TECHNICAL_REVIEW"


def test_article5_review_below_risk_threshold():
    assert classify_viability(40, blockers=1, high_risk=0, missing_controls=0) == \
        "ARTICLE_5_REVIEW_REQUIRED"


def test_high_risk_insufficient_evidence():
    assert classify_viability(50, blockers=0, high_risk=2, missing_controls=5) == \
        "HIGH_RISK_WITH_INSUFFICIENT_EVIDENCE"


def test_conditional_with_controls():
    assert classify_viability(40, blockers=0, high_risk=1, missing_controls=1) == \
        "CONDITIONALLY_VIABLE_WITH_HIGH_RISK_CONTROLS"


def test_low_signal():
    assert classify_viability(10, blockers=0, high_risk=0, missing_controls=0) == \
        "LOW_SIGNAL_NOT_A_COMPLIANCE_VERDICT"
