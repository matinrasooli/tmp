#!/usr/bin/env python3
"""Simple command-line calculator.

Supports +, -, *, /, //, %, **, unary +/-, and parentheses. Expressions are
parsed with the built-in ast module so that arbitrary Python code cannot be
executed. Only numeric literals are allowed and evaluation is safe.

Usage:
    python calculator.py "2 + 3 * 4"

If no expression is supplied on the command line, an interactive REPL is
started.
"""

from __future__ import annotations

import ast
import operator as _op
import sys
from typing import Any, Mapping

# Mapping of AST operator nodes to the corresponding Python function
_ALLOWED_BIN_OPS: Mapping[type[ast.operator], Any] = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.FloorDiv: _op.floordiv,
    ast.Mod: _op.mod,
    ast.Pow: _op.pow,
}

_ALLOWED_UNARY_OPS: Mapping[type[ast.unaryop], Any] = {
    ast.UAdd: _op.pos,
    ast.USub: _op.neg,
}


class _Evaluator(ast.NodeVisitor):
    """AST visitor that evaluates arithmetic expressions safely."""

    def visit(self, node: ast.AST) -> Any:  # type: ignore[override]
        return super().visit(node)

    # Expression root
    def visit_Expression(self, node: ast.Expression) -> Any:  # noqa: N802
        return self.visit(node.body)

    # Numeric literal (Python 3.8+: Constant, older: Num)
    def visit_Constant(self, node: ast.Constant) -> Any:  # noqa: N802
        if not isinstance(node.value, (int, float)):
            raise ValueError(f"Unsupported constant: {node.value!r}")
        return node.value

    def visit_Num(self, node: ast.Num) -> Any:  # pragma: no cover (py<3.8)
        return node.n  # type: ignore[attr-defined]

    # Binary operations
    def visit_BinOp(self, node: ast.BinOp) -> Any:  # noqa: N802
        op_type = type(node.op)
        if op_type not in _ALLOWED_BIN_OPS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _ALLOWED_BIN_OPS[op_type](left, right)

    # Unary operations
    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:  # noqa: N802
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARY_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = self.visit(node.operand)
        return _ALLOWED_UNARY_OPS[op_type](operand)

    # Parentheses are represented as nested BinOp/UnaryOp nodes, so no explicit visit

    # Disallow everything else
    def generic_visit(self, node: ast.AST) -> Any:  # noqa: N802
        raise ValueError(f"Unsupported expression component: {type(node).__name__}")


def eval_expr(expr: str) -> Any:
    """Evaluate an arithmetic expression safely and return the result."""
    parsed = ast.parse(expr, mode="eval")
    evaluator = _Evaluator()
    return evaluator.visit(parsed)


def _repl() -> None:
    """Start an interactive Read-Eval-Print Loop (REPL)."""
    print("Enter arithmetic expressions to evaluate. Type 'quit' or 'exit' to leave.")
    while True:
        try:
            line = input("calc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in {"quit", "exit"}:
            break
        if not line:
            continue
        try:
            result = eval_expr(line)
            print(result)
        except Exception as exc:
            print(f"Error: {exc}")


def main(argv: list[str] | None = None) -> None:  # noqa: D401
    """Entry point for the command-line interface."""
    argv = argv if argv is not None else sys.argv[1:]
    if argv:
        expression = " ".join(argv)
        try:
            print(eval_expr(expression))
        except Exception as exc:
            sys.exit(f"Error: {exc}")
    else:
        _repl()


if __name__ == "__main__":
    main()