"""Redaction unit tests."""

from trace_ai_act_scanner.scanning.redaction import file_hash, redact_secrets


def test_redact_api_key_assignment():
    assert "[REDACTED_SECRET]" in redact_secrets('api_key = "ABCDEFGHIJ1234567890"')


def test_redact_openai_style():
    assert "[REDACTED_SECRET]" in redact_secrets("sk-AAAAAAAAAAAAAAAAAAAAAAAA")


def test_redact_aws_access_key():
    assert "[REDACTED_SECRET]" in redact_secrets("AKIAIOSFODNN7EXAMPLE")


def test_no_change_when_clean():
    assert redact_secrets("just a normal comment") == "just a normal comment"


def test_file_hash_stable():
    a = file_hash("hello world")
    b = file_hash("hello world")
    assert a == b
    assert len(a) == 16
