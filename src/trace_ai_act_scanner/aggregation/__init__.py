"""Aggregation: risk score, readiness, viability classification."""

from trace_ai_act_scanner.aggregation.readiness import compute_readiness
from trace_ai_act_scanner.aggregation.risk import compute_risk_score
from trace_ai_act_scanner.aggregation.viability import classify_viability

__all__ = ["compute_risk_score", "compute_readiness", "classify_viability"]
