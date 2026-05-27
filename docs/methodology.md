# Methodology

This document explains what the scanner measures, what it does not, and the heuristics it uses.

## What it is

A static, name-based signal scanner. It looks for identifiers, phrases and patterns in source code and documentation that **may indicate** alignment with categories defined by the EU AI Act and GDPR. It is intended as **early-warning triage**, not as a determination of compliance.

## What it is not

- It is not legal advice.
- It does not certify compliance with Regulation (EU) 2024/1689 or with GDPR.
- It does not analyse model weights, training data or runtime behaviour.
- It does not infer intent.

A clean scan does not prove a system is compliant. A noisy scan does not prove it is non-compliant. The scanner is a starting point for legal, technical and operational review.

## Confidence

Confidence is a coarse heuristic in [0.10, 0.95]. It increases when:

- The matched term appears as a clean token (not a substring of something larger).
- The rule's `context_terms` appear in surrounding code.
- A multi-word phrase matches (vs. a single short term).

It decreases when:

- The rule's `negative_terms` appear in surrounding code.
- The match looks like a test, mock, example or demo (for Article-5 rules).
- The match is in a configuration-style negation (`uses_biometric: false`).

Confidence is **not** statistical certainty. It is a discriminator between accidental keyword collisions and likely-real signals.

## Risk score

`risk_score = min(100, sum(weight × confidence) × multiplier)`

The multiplier is derived from your `--config` file. It increases for:

- High-risk intended purposes (employment, education, credit, biometric, law enforcement…).
- EU markets.
- Provider/deployer roles under the AI Act.

## Readiness score

`readiness_score = 100 × (required_controls - missing_controls) / required_controls`

If no risk signals trigger required controls, readiness defaults to 100.

## Viability

A conservative label. Any Article-5 hit dominates everything below it. Even moderate risk with insufficient evidence trumps any low-signal classification.

## Known limitations

- Static, name-based analysis is intrinsically limited. A system can be high-risk without using any of the trigger names. Conversely, code that names something "emotion_recognition" might just be a docstring.
- Rules are biased toward English and toward Python identifiers. Other languages and natural languages are less covered.
- The redaction step protects common secret patterns but is not a substitute for treating reports as sensitive.
- The scanner does not validate `self_declaration` blocks — it forwards them as-is.

## References

- Regulation (EU) 2024/1689 (EU AI Act) — Articles 5, 50, Annex III.
- Regulation (EU) 2016/679 (GDPR) — Articles 22, 25, 35.
- ISO/IEC 42001:2023 — AI management systems.
- NIST AI Risk Management Framework (NIST AI 100-1).
