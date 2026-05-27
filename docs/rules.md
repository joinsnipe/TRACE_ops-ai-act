# Writing rules

Rules live as YAML under `src/trace_ai_act_scanner/rules/builtin/`. Each rule is a mapping:

```yaml
- id: AIII_EMPLOYMENT_WORKER_MANAGEMENT
  bucket: annex_iii_high_risk_signal
  legal_basis: "EU AI Act Annex III(4)"
  label: "Potential high-risk employment system"
  severity: HIGH_RISK_REVIEW
  weight: 32
  exact_terms:
    - cv_score
    - auto_reject
  phrases:
    - "filter cv"
    - "candidate ranking"
  context_terms: [candidate, employee, recruitment]
  required_context: []         # if non-empty, at least one of these must appear
  negative_terms: []           # if any of these appear, suppress the match
  guidance: >
    Employment AI is a core high-risk area. Check whether output materially
    affects hiring, allocation, monitoring or termination.
  contradicts_public_claims:
    - "humans make all hiring decisions"
    - "no automated CV screening"
```

## Field reference

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Unique, UPPER_SNAKE_CASE. |
| `bucket` | yes | One of: `article_5_prohibited_practice_signal`, `annex_iii_high_risk_signal`, `article_50_transparency_signal`, `gdpr_data_protection_overlap`, `governance_control`. |
| `legal_basis` | yes | Human-readable legal pointer. |
| `label` | yes | One-line description shown in reports. |
| `severity` | yes | E.g. `ARTICLE_5_REVIEW_REQUIRED`, `HIGH_RISK_REVIEW`, `TRANSPARENCY_REVIEW`, `DATA_PROTECTION_REVIEW`, `CONTROL`. |
| `weight` | yes | Integer. Use negative weights for governance controls. |
| `exact_terms` | no | Compound or atomic tokens. Atomic decomposition is tried automatically. |
| `phrases` | no | Multi-word phrases. Whitespace, `_` and `-` are treated as separators. |
| `regexes` | no | Last-resort patterns. Use sparingly. |
| `context_terms` | no | Bump confidence if these appear in surrounding context. |
| `required_context` | no | If set, at least one of these must appear or the rule does not fire. |
| `negative_terms` | no | If any of these appear, suppress the match (unless confidence is high). |
| `guidance` | no | Human-readable hint for reviewers. |
| `contradicts_public_claims` | no | **Opt-in metadata** consumed by the proprietary alignment layer. Ignored by the open-source scanner. |

## Style guide

- Prefer multi-word `phrases` over short `exact_terms`. They have fewer false positives.
- Always add `required_context` for ambiguous single words (`race`, `gender`, `score` only make sense in a specific surrounding).
- Always add `negative_terms` for common collisions (`product_filter`, `avatar_filter` near biometric rules).
- Add a positive and a negative fixture in `tests/`.
- Rules should describe **signals**, not legal verdicts.
