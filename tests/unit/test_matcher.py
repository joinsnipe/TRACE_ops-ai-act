"""Matcher unit tests."""

import pytest

from trace_ai_act_scanner.matching.matcher import match_rule
from trace_ai_act_scanner.models import Rule


@pytest.fixture
def biometric_rule():
    return Rule(
        id="TEST_BIO",
        bucket="annex_iii_high_risk_signal",
        legal_basis="EU AI Act Annex III(1)",
        label="Test biometric",
        severity="HIGH_RISK_REVIEW",
        weight=28,
        exact_terms=("face_recognition",),
        context_terms=("identify", "verify"),
    )


def test_match_exact_compound_term(biometric_rule):
    result = match_rule(biometric_rule, "face_recognition", "def face_recognition(): pass")
    assert result is not None
    matched, conf = result
    assert matched == "face_recognition"
    assert 0.10 <= conf <= 0.95


def test_match_atomic_decomposition(biometric_rule):
    result = match_rule(biometric_rule, "recognitionFace", "verify the user via recognitionFace()")
    assert result is not None


def test_no_match_when_required_context_missing():
    rule = Rule(
        id="TEST_REQ",
        bucket="article_5_prohibited_practice_signal",
        legal_basis="A5",
        label="t",
        severity="ARTICLE_5_REVIEW_REQUIRED",
        weight=10,
        exact_terms=("race",),
        required_context=("biometric",),
    )
    assert match_rule(rule, "race", "horse race results") is None


def test_negated_config_context_suppresses_match(biometric_rule):
    assert match_rule(biometric_rule, "config", "face_recognition: false") is None
    assert match_rule(biometric_rule, "config", "uses_face_recognition = false") is None
