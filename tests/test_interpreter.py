import pytest

from pylox.nodes import Binary, Expr, Literal
from pylox.interpreter import Interpreter
from pylox.tokens import EOF, Token, TokenType


@pytest.mark.parametrize(
    ("tree", "expected"),
    (
        (
            Binary(
                left=Literal(value=2.0),
                operator=Token(token_type=TokenType.PLUS, string="+", value=None),
                right=Binary(
                    left=Literal(value=3.0),
                    operator=Token(token_type=TokenType.STAR, string="*", value=None),
                    right=Literal(value=5.0),
                ),
            ),
            17.0,
        ),
        # TODO: add more tests
    ),
)
def test_interpreter(tree: Expr, expected: object) -> None:
    output = Interpreter().visit(tree)
    assert output == expected


# TODO: add failing tests
# TODO: add file tests
