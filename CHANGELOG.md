# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — Refactor and schema v1

### Added
- Restructured into installable package under `src/trace_ai_act_scanner/`.
- Rules now live as YAML under `rules/builtin/`, loadable and overridable via `--rules-dir`.
- Public JSON Schema v1 at `schema/trace-report-v1.json`; every report carries a `schema_version` field.
- Optional `self_declaration` block in the JSON output for downstream alignment analysis (narrative-vs-code).
- SARIF 2.1.0 report renderer (`--sarif` flag) for GitHub Code Scanning integration.
- `python -m trace_ai_act_scanner` entry point.
- Full test suite (unit + integration), CI matrix on Python 3.9–3.12, release-to-PyPI workflow.
- `CONTRIBUTING.md`, `SECURITY.md`, `docs/architecture.md`, `docs/rules.md`, `docs/methodology.md`, `docs/commercial-services.md`.

### Changed
- `pyproject.toml` now declares the correct package layout. `pip install .` actually works (it did not before — entry point pointed to a non-existent module).
- CLI command moved to `trace-ai-act-scan` (the old script-level entry point still works via a deprecation shim).
- Documentation reorganised under `docs/`.

### Deprecated
- The flat-file `trace_ai_act_risk_scanner.py` at the repo root is now a shim with `DeprecationWarning`. It will be removed in 0.3.0.

### Migration
- Old: `python trace_ai_act_risk_scanner.py ./my-project`
- New: `python -m trace_ai_act_scanner ./my-project` or `trace-ai-act-scan ./my-project`

## [0.1.0] — Initial release

Initial open-source release of the TRACE AI Act risk scanner.
