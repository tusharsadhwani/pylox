from __future__ import annotations

import pytest

from pylox.nodes import Binary, Expr, Grouping, Literal
from pylox.tokens import Token, TokenType
from pylox.utils.ast_printer import AstPrinter


@pytest.mark.parametrize(
    ("tree", "output"),
    (
        (
            Binary(
                left=Grouping(
                    expression=Binary(
                        left=Literal(1),
                        operator=Token(TokenType.MINUS, "-"),
                        right=Literal(2),
                    ),
                ),
                operator=Token(TokenType.PLUS, "+"),
                right=Binary(
                    left=Literal(3),
                    operator=Token(TokenType.STAR, "*"),
                    right=Literal(4),
                ),
            ),
            "((group (1 - 2)) + (3 * 4))",
        ),
    ),
)
def test_ast_printer(tree: Expr, output: str) -> None:
    tree_str = AstPrinter().visit(tree)
    assert " ".join(tree_str.split()) == " ".join(output.split())
