import os.path

import pytest

from pylox.parser import EOF, Token, TokenType, Lexer


def read_file(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


@pytest.mark.parametrize(
    ("code", "tokens"),
    (
        ("abc", [Token(TokenType.IDENTIFIER, "abc"), EOF]),
        ("nil", [Token(TokenType.NIL, "nil"), EOF]),
        ("12", [Token(TokenType.NUMBER, "12", 12), EOF]),
        ('"abc\n123"', [Token(TokenType.STRING, '"abc\n123"', "abc\n123"), EOF]),
        (
            "a=1",
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.NUMBER, "1", 1),
                EOF,
            ],
        ),
        (
            "print a.b == c",
            [
                Token(TokenType.PRINT, "print"),
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.DOT, "."),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "c"),
                EOF,
            ],
        ),
        (
            "f(x, y)",
            [
                Token(TokenType.IDENTIFIER, "f"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.COMMA, ","),
                Token(TokenType.IDENTIFIER, "y"),
                Token(TokenType.RIGHT_PAREN, ")"),
                EOF,
            ],
        ),
    ),
)
def test_lex(code: str, tokens: list[Token]) -> None:
    output = Lexer(code).tokens
    assert output == tokens


@pytest.mark.parametrize(
    ("filename", "tokens"),
    (
        (
            "simple.lox",
            [
                Token(TokenType.PRINT, "print"),
                Token(TokenType.STRING, '"Hello"', "Hello"),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.NUMBER, "5", 5.0),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.FALSE, "false"),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.PRINT, "print"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "6.75", 6.75),
                Token(TokenType.STAR, "*"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "3", 3.0),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "5", 5.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.SLASH, "/"),
                Token(TokenType.NUMBER, "2", 2.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.SEMICOLON, ";"),
                EOF,
            ],
        ),
        (
            "fibonacci.lox",
            [
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.NUMBER, "0", 0.0),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.NUMBER, "1", 1.0),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.WHILE, "while"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.LESS, "<"),
                Token(TokenType.NUMBER, "10000", 10000.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.LEFT_BRACE, "{"),
                Token(TokenType.PRINT, "print"),
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "temp"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.IDENTIFIER, "temp"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.RIGHT_BRACE, "}"),
                EOF,
            ],
        ),
    ),
)
def test_lex_files(filename: str, tokens: list[Token]) -> None:
    test_dir = os.path.join(os.path.dirname(__file__), "testdata")
    filepath = os.path.join(test_dir, filename)
    source = read_file(filepath)

    output = Lexer(source).tokens
    assert output == tokens


# TODO: add lots of failing tests, with proper error message location, etc.
# TODO: add run_interactive tests
