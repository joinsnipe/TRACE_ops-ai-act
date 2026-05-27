from pathlib import Path
from trace_ai_act_scanner.scanner import compute_report


def test_scan_example_project_detects_signals(tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text("def score_candidate_auto(resume):\n    return 0.9\n", encoding="utf-8")
    report = compute_report(str(tmp_path), {})
    assert report.summary.signals_total >= 1
    assert report.summary.potential_high_risk >= 1


def test_trace_name_does_not_trigger_biometric_categorisation(tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text("class TraceASTVisitor:\n    pass\n", encoding="utf-8")
    report = compute_report(str(tmp_path), {})
    bad = [s for s in report.signals if s.rule_id == "A5_BIOMETRIC_CATEGORISATION_SENSITIVE"]
    assert not bad
