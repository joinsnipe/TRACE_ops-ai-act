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


B2B_INDICATORS = [
    "company_", "brand_", "corporate_", "b2b", "registration_",
    "founding_date", "employees", "legal_form", "tax_id"
]


def is_likely_b2b_context(symbol: str, context: str) -> bool:
    """Check if the symbol or context strongly indicates a B2B or non-personal scope."""
    symbol_lower = symbol.lower()
    if any(ind in symbol_lower for ind in B2B_INDICATORS):
        return True
    
    # Check for dictionary keys or surrounding variables in the context
    context_lower = context.lower()
    if any(ind in context_lower for ind in B2B_INDICATORS):
        return True
        
    keys_to_check = ["company_name", "brand_name", "legal_form"]
    if any(k in context_lower for k in keys_to_check):
        return True
        
    return False


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
                continue
            
            # Semantic context exclusions
            if term_norm in rule.term_exclusions:
                exclusions = rule.term_exclusions[term_norm]
                exclude = False
                for ep in exclusions.get("exclude_if_parent", []):
                    if ep.lower() in symbol.lower():
                        exclude = True
                        break
                for ea in exclusions.get("exclude_if_assign", []):
                    if ea.lower() in symbol.lower() or ea.lower() in context.lower():
                        exclude = True
                        break
                for ec in exclusions.get("exclude_if_context", []):
                    if ec.lower() in context.lower() or ec.lower() in symbol.lower():
                        exclude = True
                        break
                if exclude:
                    continue
                    
            conf = score_confidence(rule, context, symbol, term)
            if negative_hit and conf < 0.65:
                continue
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
