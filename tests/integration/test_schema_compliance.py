"""End-to-end: scanner output must validate against schema v1."""

import json
from pathlib import Path

import jsonschema

from trace_ai_act_scanner import scan
from trace_ai_act_scanner.reporting import report_to_dict


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schema" / "trace-report-v1.json"


def test_scanner_output_validates_against_schema_v1(tmp_path):
    sample = tmp_path / "demo.py"
    sample.write_text(
        "def screen_candidates(cvs):\n"
        "    # candidate_score for recruitment\n"
        "    return [cv_score(cv) for cv in cvs]\n"
        "\n"
        "def cv_score(cv):\n"
        "    return 0.5\n",
        encoding="utf-8",
    )
    report = scan(str(tmp_path))
    payload = report_to_dict(report)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    assert payload["schema_version"] == "1.0"
    assert payload["summary"]["files_scanned"] == 1


def test_example_report_validates():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    example = json.loads((REPO_ROOT / "schema" / "trace-report-v1.example.json").read_text())
    jsonschema.validate(example, schema)
