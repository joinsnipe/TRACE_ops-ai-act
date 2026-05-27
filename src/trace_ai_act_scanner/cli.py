"""Command-line interface for the TRACE AI Act Risk Scanner."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Optional, Sequence

from trace_ai_act_scanner import __version__
from trace_ai_act_scanner.config import load_config
from trace_ai_act_scanner.reporting import render_markdown, render_sarif, report_to_dict
from trace_ai_act_scanner.scanning import scan


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trace-ai-act-scan",
        description="TRACE AI Act Risk Scanner — early-warning technical triage for EU AI Act + GDPR.",
    )
    parser.add_argument("target", help="File or directory to scan")
    parser.add_argument("--config", help="Optional JSON/YAML context file (company/system purpose)")
    parser.add_argument("--json", action="store_true", help="Print JSON report (schema v1)")
    parser.add_argument("--sarif", help="Write SARIF 2.1.0 report to path")
    parser.add_argument("--markdown", help="Write Markdown report to path")
    parser.add_argument("--max-signals", type=int, default=30, help="Max signals in Markdown report")
    parser.add_argument(
        "--no-snippets",
        action="store_true",
        help="Omit code snippets from reports to protect IP",
    )
    parser.add_argument(
        "--rules-dir",
        help="Optional directory with additional/override rules (*.yaml)",
    )
    parser.add_argument(
        "--fail-on",
        choices=["none", "article5", "high", "any"],
        default="none",
        help="Fail pipeline if risk thresholds are met",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if not os.path.exists(args.target):
        raise SystemExit(f"Target does not exist: {args.target}")

    config = load_config(args.config)
    rules_dir = Path(args.rules_dir) if args.rules_dir else None

    report = scan(
        args.target,
        config=config,
        no_snippets=args.no_snippets,
        custom_rules_dir=rules_dir,
    )

    if args.markdown:
        Path(args.markdown).write_text(
            render_markdown(report, args.max_signals), encoding="utf-8"
        )

    if args.sarif:
        Path(args.sarif).write_text(
            json.dumps(render_sarif(report), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(report_to_dict(report), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report, args.max_signals))

    # Pipeline gating.
    if args.fail_on != "none":
        if args.fail_on == "any" and report.summary.signals_total > 0:
            return 1
        if args.fail_on in {"high", "article5"} and report.summary.blockers > 0:
            return 1
        if args.fail_on == "high" and report.summary.potential_high_risk > 0:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
