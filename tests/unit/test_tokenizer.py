"""Tokenizer unit tests."""

from trace_ai_act_scanner.matching.tokenizer import line_context, split_identifier


def test_split_snake_case():
    out = split_identifier("face_recognition")
    assert "face" in out and "recognition" in out
    assert "face_recognition" in out


def test_split_camel_case():
    out = split_identifier("scoreCandidateAuto")
    assert {"score", "candidate", "auto"} <= set(out)


def test_split_kebab_case():
    out = split_identifier("auto-reject-cv")
    assert {"auto", "reject", "cv"} <= set(out)


def test_split_handles_empty():
    assert split_identifier("") == []


def test_trace_does_not_match_race():
    # Critical guarantee: 'TraceASTVisitor' must NOT yield 'race' as a token.
    out = split_identifier("TraceASTVisitor")
    assert "race" not in out
    assert "trace" in out


def test_line_context_extracts_neighbouring_lines():
    text = "line1\nline2\nline3\nline4\nline5"
    ctx = line_context(text, line_no=3, radius=1)
    assert "line2" in ctx and "line3" in ctx and "line4" in ctx
    assert "line1" not in ctx and "line5" not in ctx


def test_line_context_at_start_does_not_underflow():
    text = "a\nb\nc"
    ctx = line_context(text, line_no=1, radius=2)
    assert "a" in ctx
