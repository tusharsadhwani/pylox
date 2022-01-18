import os

import pytest

from pylox.lexer import Lexer
from pylox.nodes import ExprStmt
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
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "y"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.TRUE, "true"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "2", 2.0),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "3", 3.0),
                Token(TokenType.BANG_EQUAL, "!="),
                Token(TokenType.NUMBER, "10", 10.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.BANG_EQUAL, "!="),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "1", 1.0),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "3", 3.0),
                Token(TokenType.GREATER, ">"),
                Token(TokenType.NUMBER, "5", 5.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.EOF, ""),
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
def test_parser_exprs(tokens: list[Token], expected_tree: str) -> None:
    parser = Parser(tokens)
    program = parser.parse()

    if len(program.body) == 0:
        assert expected_tree == ""
        return

    assert len(program.body) == 1
    statement = program.body[0]
    assert isinstance(statement, ExprStmt)
    expression = statement.expression

    tree_str = AstPrinter().visit(expression)
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
    program = parser.parse()

    assert len(program.body) == 1
    statement = program.body[0]
    assert isinstance(statement, ExprStmt)
    expression = statement.expression

    tree_str = AstPrinter().visit(expression)
    assert " ".join(tree_str.split()) == " ".join(expected_tree.split())


# TODO: add failing tests
