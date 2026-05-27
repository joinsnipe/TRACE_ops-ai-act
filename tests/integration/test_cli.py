"""CLI smoke tests."""

import json
import subprocess
import sys
from pathlib import Path


def test_cli_help_runs():
    result = subprocess.run(
        [sys.executable, "-m", "trace_ai_act_scanner", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "TRACE AI Act Risk Scanner" in result.stdout


def test_cli_json_output(tmp_path: Path):
    sample = tmp_path / "demo.py"
    sample.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "trace_ai_act_scanner", str(tmp_path), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1.0"
    assert "summary" in payload
