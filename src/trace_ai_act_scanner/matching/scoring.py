"""Confidence scoring for matched signals.

Confidence is a coarse heuristic in [0.10, 0.95]. It is meant to discriminate
between accidental keyword collisions and likely-real signals, not to express
statistical certainty.
"""

from __future__ import annotations

import re

from trace_ai_act_scanner.matching.tokenizer import split_identifier
from trace_ai_act_scanner.models import Rule


def whole_word_phrase_match(phrase: str, haystack: str) -> bool:
    """Match ``phrase`` against ``haystack`` allowing space/_/- as separators."""
    escaped = re.escape(phrase.lower())
    escaped = escaped.replace(r"\ ", r"[\s_\-]+")
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", haystack.lower()))


def is_negated_config_context(matched: str, haystack: str) -> bool:
    """Detect patterns such as ``uses_biometric_data: false`` and suppress them."""
    m = re.escape(matched.lower()).replace(r"\ ", r"[\s_\-]+")
    patterns = [
        rf"{m}[a-z0-9_\-]*[^\n]{{0,100}}[:=]\s*(false|none|null|0|disabled|off|no)\b",
        rf"(no|without|disable|disabled)\s+[^\n]{{0,40}}{m}",
    ]
    return any(re.search(pattern, haystack.lower()) for pattern in patterns)


def score_confidence(rule: Rule, text: str, symbol: str, matched: str) -> float:
    """Return a confidence score in [0.10, 0.95] for a candidate match."""
    low = f"{symbol}\n{text}".lower()
    tokens = set(split_identifier(symbol) + split_identifier(text))
    confidence = 0.45

    if matched.lower() in tokens:
        confidence += 0.20
    if any(t.lower() in tokens or whole_word_phrase_match(t, low) for t in rule.context_terms):
        confidence += 0.20
    if any(t.lower() in tokens or whole_word_phrase_match(t, low) for t in rule.negative_terms):
        confidence -= 0.25
    if rule.bucket == "article_5_prohibited_practice_signal" and any(
        t in tokens for t in ("test", "mock", "example", "demo")
    ):
        confidence -= 0.10

    return max(0.10, min(0.95, round(confidence, 2)))
