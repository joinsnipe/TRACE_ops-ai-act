# Examples

This folder contains ready-to-use snippets for integrating TRACE into your workflow.

## CI integration

- `ci-integration/github-actions.yml` — GitHub Actions workflow with SARIF upload to Code Scanning.
- `ci-integration/gitlab-ci.yml` — GitLab CI job.
- `ci-integration/pre-commit-hook.sh` — local pre-commit hook that fails on Article 5 signals.

## Configs

Configs let the scanner apply context multipliers (intended purpose, market, role).

- `configs/employment_ai.json` — recruitment / worker-management.
- `configs/credit_scoring.json` — consumer credit scoring.

Use with:

```bash
trace-ai-act-scan ./my-project --config examples/configs/employment_ai.json --json
```

## Sample projects

`sample_projects/demo_app/` contains a tiny example codebase for testing the scanner end-to-end.
