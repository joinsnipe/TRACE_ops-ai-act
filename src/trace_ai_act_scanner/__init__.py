"""TRACE AI Act Risk Scanner.

Open-source technical scanner for early EU AI Act and GDPR risk signals.
"""

from .scanner import compute_report, render_markdown, report_to_dict, split_identifier

__all__ = ["compute_report", "render_markdown", "report_to_dict", "split_identifier"]
__version__ = "0.1.0"
