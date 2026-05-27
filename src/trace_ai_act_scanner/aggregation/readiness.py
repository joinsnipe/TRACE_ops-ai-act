"""Governance readiness scoring and missing-controls computation."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from trace_ai_act_scanner.models import Signal


def compute_readiness(
    signals: Sequence[Signal],
    controls: Dict[str, List[Dict[str, Any]]],
    required_controls_by_bucket: Dict[str, List[str]],
) -> Tuple[str, List[str]]:
    """Return ``(readiness_state_string, sorted list of missing control ids)``."""
    if not signals:
        return "OUT_OF_SCOPE", []
        
    required: set = set()
    for sig in signals:
        required.update(required_controls_by_bucket.get(sig.bucket, []))

    detected = {cid for cid, hits in controls.items() if hits}
    missing = sorted(cid for cid in required if cid not in detected)

    if not required:
        return "ALIGNED", missing

    detected_count = len(required) - len(missing)
    if detected_count == 0:
        return "BASELINE", missing
    elif detected_count < len(required):
        return "DEVELOPING", missing
    else:
        return "ALIGNED", missing
