"""Tokenisation, rule matching and confidence scoring."""

from trace_ai_act_scanner.matching.matcher import match_rule
from trace_ai_act_scanner.matching.scoring import (
    is_negated_config_context,
    score_confidence,
    whole_word_phrase_match,
)
from trace_ai_act_scanner.matching.tokenizer import (
    WORD_RE,
    line_context,
    split_identifier,
)

__all__ = [
    "match_rule",
    "score_confidence",
    "whole_word_phrase_match",
    "is_negated_config_context",
    "split_identifier",
    "line_context",
    "WORD_RE",
]
