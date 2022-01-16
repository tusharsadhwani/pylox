import pytest

from pylox.tokens import EOF, Token, TokenType
from pylox.parser import Parser
from pylox.utils.ast_printer import AstPrinter


def read_file(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


@pytest.mark.parametrize(
    ("tokens", "expected_tree"),
    (
        ([EOF], ""),
        ([Token(TokenType.IDENTIFIER, "abc"), EOF], "abc"),
        ([Token(TokenType.NIL, "nil"), EOF], "nil"),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "1", 1),
                EOF,
            ],
            "(a + 1)",
        ),
        (
            [
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.SLASH, "/"),
                Token(TokenType.IDENTIFIER, "y"),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "2", 2),
                Token(TokenType.STAR, "*"),
                Token(TokenType.IDENTIFIER, "z"),
                EOF,
            ],
            "((group (x / y)) + (2 * z))",
        ),
    ),
)
def test_parser(tokens: list[Token], expected_tree: str) -> None:
    parser = Parser(tokens)
    tree = parser.parse()

    tree_str = AstPrinter().visit(tree)
    assert " ".join(tree_str.split()) == " ".join(expected_tree.split())
