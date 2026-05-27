<p align="center">
  <img src="trace_logo.png" alt="TRACE Intelligence" width="280" />
</p>

# TRACE AI Act Risk Scanner

[![CI](https://github.com/joinsnipe/TRACE_ops-ai-act/actions/workflows/ci.yml/badge.svg)](https://github.com/joinsnipe/TRACE_ops-ai-act/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](pyproject.toml)
[![Schema](https://img.shields.io/badge/schema-v1.0-green)](schema/trace-report-v1.json)

> **Open-source technical scanner for early EU AI Act and GDPR risk signals.**
> Runs **locally**, on your machine, in your CI. We never see your code.

---

## What it does

`trace-ai-act-scan` walks a codebase and surfaces *signals* — names, identifiers, phrases, configuration patterns — that **may indicate** alignment with:

- **EU AI Act Article 5** — prohibited practices (manipulation, social scoring, real-time remote biometric ID, predictive policing, emotion recognition at work/school, biometric categorisation of sensitive traits).
- **EU AI Act Annex III** — high-risk systems (employment, education, credit, critical infrastructure, law enforcement, migration, justice, democratic processes).
- **EU AI Act Article 50** — synthetic content / deepfake transparency obligations.
- **GDPR** — overlap with personal data processing and profiling.
- **Governance controls** — evidence of risk management, data governance, documentation, logging, transparency, human oversight, robustness, post-market monitoring, and FRIA/DPIA.

The output is a **structured JSON report** (schema v1, see [`schema/`](schema/)), a human-readable Markdown report, and optionally SARIF for GitHub Code Scanning.

> ⚠️ **This is not legal advice and not a compliance certification.** It is technical triage. Read [`docs/legal/DISCLAIMER.md`](docs/legal/DISCLAIMER.md).

---

## Install

```bash
pip install trace-ai-act-risk-scanner
```

Or from source:

```bash
git clone https://github.com/joinsnipe/TRACE_ops-ai-act.git
cd TRACE_ops-ai-act
pip install -e ".[dev]"
```

## Use

```bash
# Quick scan, Markdown output to stdout
trace-ai-act-scan ./my-project

# Structured JSON (schema v1, suitable for downstream tools)
trace-ai-act-scan ./my-project --json > report.json

# Strip code snippets to protect IP — report contains only hashes
trace-ai-act-scan ./my-project --json --no-snippets > report.json

# Emit SARIF for GitHub Code Scanning
trace-ai-act-scan ./my-project --sarif report.sarif

# Fail CI when Article 5 signals appear
trace-ai-act-scan ./my-project --fail-on article5
```

Or programmatically:

```python
from trace_ai_act_scanner import scan
from trace_ai_act_scanner.reporting import report_to_dict

report = scan("./my-project", config={"intended_purpose": "recruitment"})
print(report.summary.viability)        # e.g. "CONDITIONALLY_VIABLE_WITH_HIGH_RISK_CONTROLS"
print(report.summary.risk_score)       # 0..100
payload = report_to_dict(report)       # schema v1 JSON-serialisable dict
```

## Output schema

Every report carries a `schema_version` field. See [`schema/trace-report-v1.json`](schema/trace-report-v1.json) for the formal contract and [`schema/README.md`](schema/README.md) for the versioning policy.

Downstream tools should validate input against this schema before processing.

---

## How it works (in 30 seconds)

```
your code  ─▶  extractors (AST + text)  ─▶  matcher  ─▶  rules (YAML)
                                                            │
                                                            ▼
                                              risk + readiness + viability
                                                            │
                                                            ▼
                                              JSON / Markdown / SARIF
```

- **Rules live in YAML** under [`src/trace_ai_act_scanner/rules/builtin/`](src/trace_ai_act_scanner/rules/builtin/). Add or override with `--rules-dir`.
- **Confidence is a heuristic in [0.10, 0.95]**, intentionally coarse: it discriminates accidental hits from likely signals, not statistical certainty.
- **Risk score** (0..100) = sum of `weight × confidence`, scaled by context multipliers from your `--config`.
- **Readiness score** (0..100) = fraction of expected governance controls actually detected for the risk buckets you trigger.
- **Viability** is a conservative label: any Article-5 hit dominates everything below it.

See [`docs/architecture.md`](docs/architecture.md) and [`docs/methodology.md`](docs/methodology.md) for details.

## What it does NOT do

- It does not certify compliance with Regulation (EU) 2024/1689 or with GDPR.
- It does not infer intent — a clean scan does not prove a system is compliant.
- It does not analyse model weights, datasets or runtime behaviour.
- It does not understand your public communication. (That requires the commercial alignment service.)

---

## Part of the TRACE Intelligence ecosystem

This scanner is the **open-source triage layer** — the first step in a broader structural intelligence infrastructure built by [TRACE Intelligence](mailto:contacto@spetrace.com).

### Consulting services

| Service line | What it covers |
|---|---|
| **Structural Diagnosis** | Courtesy audit (free), single-piece structural audit, entity diagnosis. |
| **Corporate Audit** | Full corpus audit, code audit, RAG corpus validation, forensic document audit. |
| **Operational Intelligence** | Sector-wide cartography, ecosystem mapping, contagion simulation. |
| **Institutional Operations** | Advanced services for organisations, institutions and high-demand environments. |

### Software

| Product | What it does | Access |
|---|---|---|
| **AI Act Risk Scanner** *(this repo)* | Technical signal detection in codebases. Runs locally, emits structured reports. | Open source · Apache-2.0 |
| **BrandRank™** | Monitors how AI models (ChatGPT, Claude, Gemini, Perplexity) represent your organisation over time. Tracks mention rate, sentiment, competitive positioning and semantic drift. | 15-day free trial |

### SIO™ — Structural Intelligence Optimization

All consulting services operate under **SIO™**, our structural intelligence methodology. SIO™ audits and corrects the structure from which AI systems understand an organisation — measuring God Nodes, cohesion, fragmentation, semantic gaps and crisis resilience using graph topology and multi-LLM triangulation.

The scanner tells you **what your code does**. Our consulting services tell you whether what your company *says publicly* is consistent with what your code *actually does* — and whether AI systems are structurally understanding your organisation as intended.

> The open-source scanner is and will remain **fully functional on its own**, free under Apache-2.0. The premium services add qualified human analysis and proprietary structural intelligence — they are not gated behind missing features.

📧 **[contacto@spetrace.com](mailto:contacto@spetrace.com)**

---

## Contributing

We welcome contributions, especially on rules. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

Security issues → [`SECURITY.md`](SECURITY.md).

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`docs/legal/NOTICE.md`](docs/legal/NOTICE.md).

