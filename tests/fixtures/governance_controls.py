"""Demo governance controls — synthetic fixture."""


def audit_log(event: dict) -> None:
    """Write to the traceability record. Detects CTRL_LOGGING_RECORDKEEPING."""
    pass


def human_review(decision: dict) -> bool:
    """Manual review with override and appeal. Detects CTRL_HUMAN_OVERSIGHT."""
    return True


def risk_management_register() -> list:
    """Risk register. Detects CTRL_RISK_MANAGEMENT."""
    return []
