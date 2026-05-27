# TRACE Scanner Report — JSON Schema

This folder defines the **public output contract** for the TRACE AI Act Risk Scanner.

It is the wire format consumed by downstream tooling — including the proprietary [SPE Audit Reporting](https://github.com/joinsnipe/TRACE_ops-ai-act#commercial-services) layer that performs **narrative-vs-code alignment**.

## Current version

**`trace-report-v1.json`** — JSON Schema Draft 2020-12, schema version `1.0`.

## Versioning policy (semver)

- **`v1.x`** — additive only. New optional fields can appear; existing consumers keep working unchanged.
- **`v2.0`** — breaking. Will be published in parallel to v1 for at least 6 months before v1 is deprecated.

Every report emitted by the scanner carries a top-level `schema_version` field. Downstream consumers should validate against this field and refuse to process unknown major versions.

## Validating a report

```bash
pip install jsonschema
python -c "
import json, jsonschema
schema = json.load(open('schema/trace-report-v1.json'))
report = json.load(open('my-report.json'))
jsonschema.validate(report, schema)
print('OK')
"
```

## The `self_declaration` block

The `self_declaration` block is **optional** and lets the scanned organisation publish:

- The intended purpose of the AI system.
- Verbatim public claims (from the company website, policies, marketing).
- URLs where those claims are made.
- Deployment context, operator role, target market.

This block is **the input the alignment analysis uses to cross-check whether what the organisation says publicly matches what the code does technically**. The open-source scanner does not perform this cross-check — it simply forwards the declaration. The SPE Audit Reporting service does.

Example: see [`trace-report-v1.example.json`](trace-report-v1.example.json).
