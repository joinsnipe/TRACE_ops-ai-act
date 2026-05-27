"""Load optional context/config files in JSON or YAML."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_config(path: Optional[str]) -> Dict[str, Any]:
    """Load a JSON or YAML context file. Empty if ``path`` is None."""
    if not path:
        return {}
    p = Path(path)
    data = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(data) or {}
    return json.loads(data)
