"""Mechanism to ignore specific signals based on a .traceignore file."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from trace_ai_act_scanner.models import Signal

log = logging.getLogger(__name__)

def load_ignores(target_root: Path) -> List[Dict]:
    """Load and parse .traceignore JSON from the target directory if it exists."""
    # Find the root of the project to locate .traceignore
    root = target_root if target_root.is_dir() else target_root.parent
    ignore_path = root / ".traceignore"
    if not ignore_path.exists():
        return []
    
    try:
        data = json.loads(ignore_path.read_text(encoding="utf-8"))
        ignores = data.get("ignores", [])
        if not isinstance(ignores, list):
            log.warning(".traceignore 'ignores' key must be a list.")
            return []
        log.info("Loaded %d ignore rules from .traceignore", len(ignores))
        return ignores
    except Exception as exc:
        log.warning("Failed to parse .traceignore: %s", exc)
        return []

def filter_signals(signals: List[Signal], ignores: List[Dict]) -> Tuple[List[Signal], List[Dict[str, Any]]]:
    """Return (active_signals, silenced_signals_details)."""
    if not ignores:
        return signals, []
        
    filtered = []
    silenced = []
    for sig in signals:
        should_ignore = False
        ignore_reason = ""
        for rule in ignores:
            match_rule_id = rule.get("rule_id") == sig.rule_id if "rule_id" in rule else True
            match_file = str(rule.get("file")) in sig.file if "file" in rule else True
            match_line = rule.get("line") == sig.line if "line" in rule else True
            
            # A rule must specify at least something to match, and all specified conditions must be true
            if match_rule_id and match_file and match_line and any(k in rule for k in ("rule_id", "file", "line")):
                should_ignore = True
                ignore_reason = rule.get("reason", "No reason provided in .traceignore")
                break
                
        if not should_ignore:
            filtered.append(sig)
        else:
            silenced.append({
                "rule_id": sig.rule_id,
                "file": sig.file,
                "line": sig.line,
                "reason": ignore_reason
            })
            
    return filtered, silenced
