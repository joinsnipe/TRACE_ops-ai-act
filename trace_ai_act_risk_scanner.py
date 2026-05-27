#!/usr/bin/env python3
"""Backward-compatibility shim for the legacy flat-file entry point.

Older versions exposed the scanner as a single ``trace_ai_act_risk_scanner.py``
file at the repository root. As of v0.2.0 the scanner lives inside the
``trace_ai_act_scanner`` package under ``src/``. This shim keeps existing CI
pipelines working but emits a ``DeprecationWarning``. It will be removed in
v0.3.0.

Migrate to one of:
    python -m trace_ai_act_scanner /path/to/code
    trace-ai-act-scan /path/to/code            # after `pip install .`
"""

from __future__ import annotations

import warnings

warnings.warn(
    "`trace_ai_act_risk_scanner.py` is deprecated and will be removed in v0.3.0. "
    "Use `python -m trace_ai_act_scanner` or the `trace-ai-act-scan` command instead.",
    DeprecationWarning,
    stacklevel=2,
)

from trace_ai_act_scanner.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
