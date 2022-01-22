import pytest

from pylox.interpreter import Interpreter
from pylox.nodes import Binary, Expr, Literal, Print, Program, VarDeclaration, Variable
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
def test_interpreter_expr(tree: Expr, expected: object) -> None:
    output = Interpreter().visit(tree)
    assert output == expected


@pytest.mark.parametrize(
    ("tree", "output"),
    (
        (
            Program(
                body=[
                    VarDeclaration(
                        name=Token(TokenType.IDENTIFIER, "greeting"),
                        initializer=Literal("hello lox!"),
                    ),
                    Print(Variable(Token(TokenType.IDENTIFIER, "greeting"))),
                ]
            ),
            "hello lox!",
        ),
        # TODO: add more tests
    ),
)
def test_interpreter(
    tree: Program,
    output: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    Interpreter().visit(tree)

    stdout, stderr = capsys.readouterr()
    assert stdout.rstrip() == output
    assert stderr == ""


# TODO: add failing tests
# TODO: add file tests
