import os
import pytest

from pylox.lexer import Lexer
from pylox.parser import Parser
from pylox.tokens import EOF, Token, TokenType
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
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "c"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "5"),
                EOF,
            ],
            "(((a == b) == c) == 5)",
        ),
        (
            [
                Token(TokenType.IDENTIFIER, string="x", value=None),
                Token(TokenType.EQUAL_EQUAL, string="==", value=None),
                Token(TokenType.IDENTIFIER, string="y", value=None),
                Token(TokenType.EQUAL_EQUAL, string="==", value=None),
                Token(TokenType.TRUE, string="true", value=None),
                Token(TokenType.EQUAL_EQUAL, string="==", value=None),
                Token(TokenType.LEFT_PAREN, string="(", value=None),
                Token(TokenType.LEFT_PAREN, string="(", value=None),
                Token(TokenType.NUMBER, string="2", value=2.0),
                Token(TokenType.PLUS, string="+", value=None),
                Token(TokenType.NUMBER, string="3", value=3.0),
                Token(TokenType.BANG_EQUAL, string="!=", value=None),
                Token(TokenType.NUMBER, string="10", value=10.0),
                Token(TokenType.RIGHT_PAREN, string=")", value=None),
                Token(TokenType.BANG_EQUAL, string="!=", value=None),
                Token(TokenType.LEFT_PAREN, string="(", value=None),
                Token(TokenType.NUMBER, string="1", value=1.0),
                Token(TokenType.PLUS, string="+", value=None),
                Token(TokenType.NUMBER, string="3", value=3.0),
                Token(TokenType.GREATER, string=">", value=None),
                Token(TokenType.NUMBER, string="5", value=5.0),
                Token(TokenType.RIGHT_PAREN, string=")", value=None),
                Token(TokenType.RIGHT_PAREN, string=")", value=None),
                Token(TokenType.EOF, string="", value=None),
            ],
            """
            (((x == y) == true) == 
                (group
                    ((group ((2.0 + 3.0) != 10.0))
                    !=
                    (group ((1.0 + 3.0) > 5.0)))))
            """,
        ),
    ),
)
def test_parser(tokens: list[Token], expected_tree: str) -> None:
    parser = Parser(tokens)
    tree = parser.parse()

    tree_str = AstPrinter().visit(tree)
    assert " ".join(tree_str.split()) == " ".join(expected_tree.split())


@pytest.mark.parametrize(
    ("filename", "expected_tree"),
    (
        (
            "expression.lox",
            "(2.0 + (3.0 * 5.0))",
        ),
        (
            "expression_long.lox",
            """
            ((group
                ((((2.0 > 3.0) > (4.0 + 5.0)) != x) == ((y * z) / w)))
                == (false + true))
            """,
        ),
    ),
)
def test_parser_files(filename: str, expected_tree: str) -> None:
    test_dir = os.path.join(os.path.dirname(__file__), "testdata")
    filepath = os.path.join(test_dir, filename)
    source = read_file(filepath)

    tokens = Lexer(source).tokens
    parser = Parser(tokens)
    tree = parser.parse()

    tree_str = AstPrinter().visit(tree)
    assert " ".join(tree_str.split()) == " ".join(expected_tree.split())


# TODO: add failing tests
