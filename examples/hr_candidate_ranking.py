"""Example intentionally containing AI Act review signals."""


def score_candidate_auto(resume_text: str, interview_notes: str) -> float:
    """Automated candidate ranking for recruitment workflows."""
    return 0.87


def filter_cv_auto(candidate_profile: dict) -> bool:
    # Human review should exist before rejecting a natural person.
    return candidate_profile.get("score", 0) > 0.6


def audit_log(event: dict) -> None:
    print(event)
