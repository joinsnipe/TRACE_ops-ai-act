"""Load rules from YAML files into :class:`Rule` dataclasses.

Builtin rules live under ``rules/builtin/`` and are bundled in the wheel.
Custom rule directories can be passed via the CLI ``--rules-dir`` flag and
are merged on top of the builtins (custom rules with the same ``id``
override builtins, with a warning).
"""

from __future__ import annotations

import logging
from importlib import resources
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml

from trace_ai_act_scanner.models import Rule

log = logging.getLogger(__name__)

# Files under rules/builtin/ that contain risk and control rules.
_BUILTIN_FILES = (
    "article_5.yaml",
    "annex_iii.yaml",
    "article_50.yaml",
    "gdpr.yaml",
    "controls.yaml",
)

_REQUIRED_CONTROLS_FILE = "required_controls.yaml"


def _rule_from_dict(data: dict) -> Rule:
    """Build a :class:`Rule` from a YAML mapping with safe defaults."""
    return Rule(
        id=data["id"],
        bucket=data["bucket"],
        legal_basis=data["legal_basis"],
        label=data["label"],
        severity=data["severity"],
        weight=int(data["weight"]),
        exact_terms=tuple(data.get("exact_terms") or ()),
        phrases=tuple(data.get("phrases") or ()),
        regexes=tuple(data.get("regexes") or ()),
        context_terms=tuple(data.get("context_terms") or ()),
        required_context=tuple(data.get("required_context") or ()),
        negative_terms=tuple(data.get("negative_terms") or ()),
        guidance=(data.get("guidance") or "").strip(),
        contradicts_public_claims=tuple(data.get("contradicts_public_claims") or ()),
    )


def _load_yaml_text(text: str) -> Iterable[dict]:
    parsed = yaml.safe_load(text) or []
    if not isinstance(parsed, list):
        raise ValueError("Rule YAML must be a list of mappings at the top level")
    return parsed


def load_builtin_rules() -> Tuple[List[Rule], List[Rule]]:
    """Return ``(risk_rules, control_rules)`` from the bundled YAML files."""
    risk: List[Rule] = []
    controls: List[Rule] = []
    base = resources.files("trace_ai_act_scanner").joinpath("rules", "builtin")
    for name in _BUILTIN_FILES:
        text = base.joinpath(name).read_text(encoding="utf-8")
        for raw in _load_yaml_text(text):
            rule = _rule_from_dict(raw)
            (controls if rule.bucket == "governance_control" else risk).append(rule)
    return risk, controls


def load_required_controls() -> Dict[str, List[str]]:
    """Return the mapping bucket -> [control_id, ...]."""
    base = resources.files("trace_ai_act_scanner").joinpath("rules")
    text = base.joinpath(_REQUIRED_CONTROLS_FILE).read_text(encoding="utf-8")
    parsed = yaml.safe_load(text) or {}
    return {str(k): list(v or []) for k, v in parsed.items()}


def load_custom_rules(directory: Path) -> Tuple[List[Rule], List[Rule]]:
    """Load custom rules from a user-provided directory.

    Files with extensions ``.yaml`` or ``.yml`` are read. Any rule with the
    same ``id`` as a builtin will be flagged at the merge step.
    """
    risk: List[Rule] = []
    controls: List[Rule] = []
    if not directory.is_dir():
        raise FileNotFoundError(f"Custom rules directory not found: {directory}")
    for path in sorted(directory.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        for raw in _load_yaml_text(text):
            rule = _rule_from_dict(raw)
            (controls if rule.bucket == "governance_control" else risk).append(rule)
    return risk, controls


def merge_rules(builtin: List[Rule], custom: List[Rule]) -> List[Rule]:
    """Merge builtin and custom rules; custom overrides builtin by ``id``."""
    by_id: Dict[str, Rule] = {r.id: r for r in builtin}
    for r in custom:
        if r.id in by_id:
            log.warning("Custom rule %s overrides a builtin rule", r.id)
        by_id[r.id] = r
    return list(by_id.values())
