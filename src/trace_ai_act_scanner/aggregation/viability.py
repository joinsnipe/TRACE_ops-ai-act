"""Classify a scan into a coarse viability category.

The category drives the headline label users see in the CLI and JSON output.
It is intentionally conservative: the bar for a clean "low signal" label is
high, and an Article 5 hit always trumps everything else.
"""

from __future__ import annotations


def classify_viability(
    risk_score: int,
    blockers: int,
    high_risk: int,
    missing_controls: int,
) -> str:
    """Return the viability label for the scan."""
    if blockers > 0 and risk_score >= 70:
        return "BLOCKED_UNTIL_LEGAL_AND_TECHNICAL_REVIEW"
    if blockers > 0:
        return "ARTICLE_5_REVIEW_REQUIRED"
    if high_risk > 0 and missing_controls >= 4:
        return "HIGH_RISK_WITH_INSUFFICIENT_EVIDENCE"
    if high_risk > 0:
        return "CONDITIONALLY_VIABLE_WITH_HIGH_RISK_CONTROLS"
    if risk_score >= 35:
        return "MODERATE_RISK_REVIEW_REQUIRED"
    return "LOW_SIGNAL_NOT_A_COMPLIANCE_VERDICT"
