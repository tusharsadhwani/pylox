import os.path

import pytest

from pylox.parser import EOF, Token, TokenType, lex


def read_file(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


@pytest.mark.parametrize(
    ("code", "tokens"),
    (("abc", [Token(TokenType.IDENTIFIER, "abc"), EOF]),),
)
def test_lex(code: str, tokens: list[Token]) -> None:
    output = lex(code)
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

    output = lex(source)
    assert output == tokens


# TODO: add lots of failing tests, with proper error message location, etc.
# TODO: add run_interactive tests
