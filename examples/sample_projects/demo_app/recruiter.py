"""Tiny demo app — a candidate-screening tool. Intentionally triggers signals."""

from typing import List


def cv_score(candidate: dict) -> float:
    """Score a CV. Triggers AIII_EMPLOYMENT_WORKER_MANAGEMENT."""
    return float(len(candidate.get("experience", [])))


def auto_reject(candidate: dict) -> bool:
    """Auto-reject below threshold. Triggers AIII_EMPLOYMENT_WORKER_MANAGEMENT."""
    return cv_score(candidate) < 2.0


def filter_cv(candidates: List[dict]) -> List[dict]:
    """Filter CVs. The phrase 'filter cv' matches a phrase rule."""
    return [c for c in candidates if not auto_reject(c)]
