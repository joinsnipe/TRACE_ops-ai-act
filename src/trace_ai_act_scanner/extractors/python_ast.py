"""Extractor for Python source files using AST.

Falls back to the line-based text extractor when the file does not parse
(e.g. partial files, Python 2 syntax, generated code).
"""

from __future__ import annotations

import ast
import logging
from typing import Any, List, Tuple

from trace_ai_act_scanner.extractors.base import ExtractedItem
from trace_ai_act_scanner.extractors.text import extract_text_items
from trace_ai_act_scanner.matching.tokenizer import line_context

log = logging.getLogger(__name__)


class _PythonASTVisitor(ast.NodeVisitor):
    def __init__(self, source: str) -> None:
        self.source = source
        self.items: List[ExtractedItem] = []

    def _add(self, symbol: str, node: ast.AST, node_type: str) -> None:
        if not symbol:
            return
        line = getattr(node, "lineno", 1) or 1
        self.items.append((symbol, line, node_type, line_context(self.source, line)))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self._add(node.name, node, "FunctionDef")
        for arg in node.args.args + node.args.kwonlyargs:
            self._add(arg.arg, arg, "Argument")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self._add(node.name, node, "ClassDef")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Name):
            self._add(node.func.id, node, "Call")
        elif isinstance(node.func, ast.Attribute):
            self._add(node.func.attr, node, "CallAttribute")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        self._add(node.id, node, "Name")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        self._add(node.attr, node, "Attribute")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            self._add(alias.name, node, "Import")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        if node.module:
            self._add(node.module, node, "ImportFrom")
        for alias in node.names:
            self._add(alias.name, node, "ImportFrom")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, str) and len(node.value) <= 500:
            self._add(node.value, node, "StringLiteral")
        self.generic_visit(node)


def extract_python_items(source: str, filename: str = "<unknown>") -> List[ExtractedItem]:
    """Extract symbols from Python ``source`` using AST + text fallback."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        log.debug("Python AST parse failed for %s (%s); falling back to text", filename, exc)
        return extract_text_items(source)
    visitor = _PythonASTVisitor(source)
    visitor.visit(tree)
    # Also include the text scan so comments and config-like strings are caught.
    return visitor.items + extract_text_items(source)
