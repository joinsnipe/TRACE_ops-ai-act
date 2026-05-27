# Contributing to TRACE AI Act Risk Scanner

Thanks for your interest. This project is a community resource for early EU AI Act and GDPR risk triage. Contributions are welcome, especially on rules.

## Quick start

```bash
git clone https://github.com/joinsnipe/TRACE_ops-ai-act.git
cd TRACE_ops-ai-act
pip install -e ".[dev]"
pytest -q
ruff check src tests
```

## Adding a rule

Rules live as YAML under `src/trace_ai_act_scanner/rules/builtin/`. To add one:

1. Pick the right file (`article_5.yaml`, `annex_iii.yaml`, `article_50.yaml`, `gdpr.yaml`, or `controls.yaml`).
2. Append a new entry following the existing shape. Required fields: `id`, `bucket`, `legal_basis`, `label`, `severity`, `weight`.
3. Prefer `phrases` and compound `exact_terms` over short single words to reduce false positives.
4. Add `required_context` for ambiguous terms (e.g. `race` only makes sense alongside `biometric`).
5. Add `negative_terms` to suppress obvious false-positive contexts.
6. Add a `guidance` field — one or two lines on what a reviewer should check.
7. Optionally add `contradicts_public_claims` — short claims this signal typically contradicts. This is consumed by the proprietary alignment layer; the open-source scanner ignores it but rule readers benefit from the documentation.
8. Add at least one positive and one negative fixture in `tests/`.

## Pull requests

- Keep PRs focused. One rule per PR is fine.
- Run `pytest -q` and `ruff check src tests` before pushing.
- For new public API, add or update a docstring.
- For schema changes, bump the schema version following the policy in `schema/README.md`.

## What we will not accept

- Rules that read as moral judgements rather than technical signals.
- Rules with no `guidance` field.
- Detection logic that requires network calls at scan time.
- Anything that produces output not validating against the published JSON Schema.

## Code of conduct

Be excellent to each other. Personal attacks, harassment or discriminatory language will result in immediate removal.
