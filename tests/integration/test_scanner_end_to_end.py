"""Integration test: scanner detects expected buckets on synthetic fixtures."""

from trace_ai_act_scanner import scan


def test_employment_recruitment_triggers_annex_iii(tmp_path):
    (tmp_path / "recruiter.py").write_text(
        "def filter_cv(candidate):\n"
        "    score = cv_score(candidate)\n"
        "    if score < 0.4:\n"
        "        return auto_reject(candidate)\n"
        "    return candidate\n",
        encoding="utf-8",
    )
    report = scan(str(tmp_path), config={"intended_purpose": "recruitment"})
    buckets = {s.bucket for s in report.signals}
    assert "annex_iii_high_risk_signal" in buckets


def test_clean_code_low_signal(tmp_path):
    (tmp_path / "calculator.py").write_text(
        "def add(a, b):\n    return a + b\n\n"
        "def multiply(a, b):\n    return a * b\n",
        encoding="utf-8",
    )
    report = scan(str(tmp_path))
    assert report.summary.blockers == 0
    assert report.summary.viability in {
        "LOW_SIGNAL_NOT_A_COMPLIANCE_VERDICT",
        "MODERATE_RISK_REVIEW_REQUIRED",
    }


def test_governance_controls_detected(tmp_path):
    (tmp_path / "governance.md").write_text(
        "# Our AI governance\n\n"
        "We maintain a risk management system, model cards, audit logs, "
        "human oversight, adversarial testing, post-market monitoring, "
        "and a fundamental rights impact assessment (FRIA).\n",
        encoding="utf-8",
    )
    report = scan(str(tmp_path))
    assert report.summary.governance_controls_detected >= 4
