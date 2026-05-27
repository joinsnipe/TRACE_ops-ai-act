"""Governance readiness scoring and missing-controls computation."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from trace_ai_act_scanner.models import Signal


def compute_readiness(
    signals: Sequence[Signal],
    silenced_signals: Sequence[Dict[str, Any]],
    controls: Dict[str, List[Dict[str, Any]]],
    required_controls_by_bucket: Dict[str, List[str]],
) -> Tuple[str, List[str]]:
    """Return ``(readiness_state_string, sorted list of missing control ids)``."""
    signals_total = len(signals)
    silenced_count = len(silenced_signals)
    
    required: set = set()
    for s in signals:
        if s.bucket in required_controls_by_bucket:
            required.update(required_controls_by_bucket[s.bucket])
            
    detected = set(controls.keys())
    missing = sorted(list(required - detected))

    detected_count = len(required) - len(missing)
    if signals_total == 0 and silenced_count == 0:
        return "OUT_OF_SCOPE", missing
    if signals_total == 0 and silenced_count > 0:
        return "REVIEWED_NO_ACTION", missing
    if signals_total > 0 and silenced_count > 0:
        return "REVIEW_WITH_EXCEPTIONS", missing
        
    if detected_count == 0 and required:
        return "BASELINE", missing
    if missing:
        return "DEVELOPING", missing
    return "ALIGNED", missing
