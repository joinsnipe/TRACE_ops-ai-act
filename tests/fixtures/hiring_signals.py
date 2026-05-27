"""Demo hiring screen — synthetic fixture with intentional high-risk signals."""


def score_candidate_auto(cv: dict, role: str) -> float:
    """Auto-score a candidate. Intentional Annex III(4) signal."""
    return rank_candidate(cv, role)


def rank_candidate(cv: dict, role: str) -> float:
    return 0.5


def auto_reject(score: float) -> bool:
    """Auto-reject below threshold. Intentional Annex III(4) signal."""
    return score < 0.3
