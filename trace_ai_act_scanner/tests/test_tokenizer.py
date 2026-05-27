from trace_ai_act_scanner.scanner import split_identifier


def test_trace_does_not_match_race_token():
    tokens = split_identifier("TraceASTVisitor")
    assert "race" not in tokens
    assert "trace" in tokens


def test_snake_case_compound_is_preserved():
    tokens = split_identifier("face_recognition")
    assert "face" in tokens
    assert "recognition" in tokens
    assert "face_recognition" in tokens
