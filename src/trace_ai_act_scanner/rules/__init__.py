"""Rule loading and management.

Builtin rules ship as YAML under :mod:`trace_ai_act_scanner.rules.builtin`
and are loaded at startup. Users can supply additional rules via
``--rules-dir``.
"""

from trace_ai_act_scanner.rules.loader import (
    load_builtin_rules,
    load_custom_rules,
    load_required_controls,
    merge_rules,
)

__all__ = [
    "load_builtin_rules",
    "load_custom_rules",
    "load_required_controls",
    "merge_rules",
]
