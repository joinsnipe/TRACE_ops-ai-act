"""Rule matcher.

Given a ``symbol`` (an identifier or string literal) and its surrounding
``context``, decide whether a given :class:`Rule` fires and with what
confidence.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

from trace_ai_act_scanner.matching.scoring import (
    is_negated_config_context,
    score_confidence,
    whole_word_phrase_match,
)
from trace_ai_act_scanner.matching.tokenizer import split_identifier
from trace_ai_act_scanner.models import Rule


def match_rule(rule: Rule, symbol: str, context: str) -> Optional[Tuple[str, float]]:
    """Apply ``rule`` to ``symbol`` + ``context``.

    Returns ``(matched_text, confidence)`` if the rule fires, ``None`` otherwise.
    """
    tokens = set(split_identifier(symbol) + split_identifier(context))
    haystack = f"{symbol}\n{context}".lower()

    if rule.required_context and not any(
        t.lower() in tokens or whole_word_phrase_match(t, haystack)
        for t in rule.required_context
    ):
        return None

    negative_hit = any(
        t.lower() in tokens or whole_word_phrase_match(t, haystack)
        for t in rule.negative_terms
    )

    # 1) Exact terms (or atomic-token decomposition).
    for term in rule.exact_terms:
        term_norm = term.lower()
        term_tokens = split_identifier(term_norm)
        atomic_term_tokens = [t for t in term_tokens if t != term_norm]
        if term_norm in tokens or (
            atomic_term_tokens and all(t in tokens for t in atomic_term_tokens)
        ):
            if is_negated_config_context(term, haystack):
                return None
            conf = score_confidence(rule, context, symbol, term)
            if negative_hit and conf < 0.65:
                return None
            return term, conf

    # 2) Phrases.
    for phrase in rule.phrases:
        if whole_word_phrase_match(phrase, haystack):
            if is_negated_config_context(phrase, haystack):
                return None
            conf = score_confidence(rule, context, symbol, phrase) + 0.05
            return phrase, min(0.95, round(conf, 2))

    # 3) Regexes (last resort, lowest priority).
    for pattern in rule.regexes:
        if re.search(pattern, haystack, flags=re.IGNORECASE):
            conf = score_confidence(rule, context, symbol, pattern) + 0.05
            return pattern, min(0.95, round(conf, 2))

    return None
