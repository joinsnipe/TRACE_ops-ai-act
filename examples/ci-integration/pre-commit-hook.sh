#!/usr/bin/env bash
# Pre-commit hook: refuse a commit that introduces Article 5 signals.
# Install: cp examples/ci-integration/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

if ! command -v trace-ai-act-scan >/dev/null 2>&1; then
  echo "trace-ai-act-scan not found. Install: pip install trace-ai-act-risk-scanner" >&2
  exit 1
fi

trace-ai-act-scan . --fail-on article5 --no-snippets >/dev/null
