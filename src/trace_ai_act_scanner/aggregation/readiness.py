"""Governance readiness scoring and missing-controls computation."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from trace_ai_act_scanner.models import Signal


def compute_readiness(
    signals: Sequence[Signal],
    controls: Dict[str, List[Dict[str, Any]]],
    required_controls_by_bucket: Dict[str, List[str]],
) -> Tuple[int, List[str]]:
    """Return ``(readiness_score 0..100, sorted list of missing control ids)``."""
    required: set = set()
    for sig in signals:
        required.update(required_controls_by_bucket.get(sig.bucket, []))

    detected = {cid for cid, hits in controls.items() if hits}
    missing = sorted(cid for cid in required if cid not in detected)

    if not required:
        return 100, missing

    score = int(round(100 * (len(required) - len(missing)) / len(required)))
    return score, missing
