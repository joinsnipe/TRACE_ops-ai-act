# Architecture

The scanner is a small pipeline. Each stage has a single responsibility and is testable in isolation.

```
┌────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Walker    │────▶│  Extractors  │────▶│   Matcher   │────▶│  Aggregation │
│  (files)   │     │  (AST/text)  │     │  (rules)    │     │  risk + ctrl │
└────────────┘     └──────────────┘     └─────────────┘     └──────┬───────┘
                                                                   │
                                                                   ▼
                                                         ┌──────────────────┐
                                                         │     Reporting    │
                                                         │  JSON/MD/SARIF   │
                                                         └──────────────────┘
```

## Modules

- `scanning.walker` — discovers files under the target, honouring excludes and supported extensions.
- `extractors.python_ast` — emits `(symbol, line, node_type, context)` tuples from Python via AST.
- `extractors.text` — line/word fallback for everything else (Markdown, YAML, JSON, JS, etc.).
- `matching.tokenizer` — splits identifiers safely (`face_recognition` → `[face, recognition, face_recognition]`).
- `matching.matcher` — applies a `Rule` to a `(symbol, context)` pair. Honours `required_context`, `negative_terms`, exact terms, phrases, and regexes (in that order).
- `matching.scoring` — computes a coarse confidence in [0.10, 0.95].
- `aggregation.risk` — confidence-weighted sum × context multipliers, capped at 100.
- `aggregation.readiness` — fraction of required controls actually detected for the buckets triggered.
- `aggregation.viability` — a conservative label. Any Article-5 hit dominates.
- `reporting.json_report` — emits schema-v1-conformant JSON.
- `reporting.markdown_report` — emits Markdown.
- `reporting.sarif_report` — emits SARIF 2.1.0 for GitHub Code Scanning.

## Why this shape

- **Rules in YAML** so legal/compliance teams can review and propose changes without Python.
- **Schema-versioned output** so downstream tools (notably the proprietary SPE Audit Reporting layer) can validate and route safely.
- **Extractor protocol** so adding JS/TS/Java extractors is a matter of implementing one function.
- **Aggregation split into three modules** so risk/readiness/viability can evolve independently and be reasoned about separately by reviewers.
