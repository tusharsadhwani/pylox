import os.path

import pytest

from pylox.parser import Token, TokenType, lex


def read_file(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


@pytest.mark.parametrize(
    ("filename", "tokens"),
    (
        (
            "simple.lox",
            [
                Token(TokenType.PRINT, "print", None),
                Token(TokenType.STRING, '"Hello"', "Hello"),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.VAR, "var", None),
                Token(TokenType.IDENTIFIER, "a", None),
                Token(TokenType.EQUAL, "=", None),
                Token(TokenType.NUMBER, "5", 5.0),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.IDENTIFIER, "a", None),
                Token(TokenType.EQUAL, "=", None),
                Token(TokenType.FALSE, "false", None),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.PRINT, "print", None),
                Token(TokenType.LEFT_PAREN, "(", None),
                Token(TokenType.NUMBER, "6.75", 6.75),
                Token(TokenType.STAR, "*", None),
                Token(TokenType.LEFT_PAREN, "(", None),
                Token(TokenType.NUMBER, "3", 3.0),
                Token(TokenType.PLUS, "+", None),
                Token(TokenType.NUMBER, "5", 5.0),
                Token(TokenType.RIGHT_PAREN, ")", None),
                Token(TokenType.SLASH, "/", None),
                Token(TokenType.NUMBER, "2", 2.0),
                Token(TokenType.RIGHT_PAREN, ")", None),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.EOF, "", None),
            ],
        ),
        (
            "fibonacci.lox",
            [
                Token(TokenType.VAR, "var", None),
                Token(TokenType.IDENTIFIER, "a", None),
                Token(TokenType.EQUAL, "=", None),
                Token(TokenType.NUMBER, "0", 0.0),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.VAR, "var", None),
                Token(TokenType.IDENTIFIER, "b", None),
                Token(TokenType.EQUAL, "=", None),
                Token(TokenType.NUMBER, "1", 1.0),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.WHILE, "while", None),
                Token(TokenType.LEFT_PAREN, "(", None),
                Token(TokenType.IDENTIFIER, "a", None),
                Token(TokenType.LESS, "<", None),
                Token(TokenType.NUMBER, "10000", 10000.0),
                Token(TokenType.RIGHT_PAREN, ")", None),
                Token(TokenType.LEFT_BRACE, "{", None),
                Token(TokenType.PRINT, "print", None),
                Token(TokenType.IDENTIFIER, "a", None),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.VAR, "var", None),
                Token(TokenType.IDENTIFIER, "temp", None),
                Token(TokenType.EQUAL, "=", None),
                Token(TokenType.IDENTIFIER, "a", None),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.IDENTIFIER, "a", None),
                Token(TokenType.EQUAL, "=", None),
                Token(TokenType.IDENTIFIER, "b", None),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.IDENTIFIER, "b", None),
                Token(TokenType.EQUAL, "=", None),
                Token(TokenType.IDENTIFIER, "temp", None),
                Token(TokenType.PLUS, "+", None),
                Token(TokenType.IDENTIFIER, "b", None),
                Token(TokenType.SEMICOLON, ";", None),
                Token(TokenType.RIGHT_BRACE, "}", None),
                Token(TokenType.EOF, "", None),
            ],
        ),
    ),
)
def test_lex(filename: str, tokens: list[Token]) -> None:
    test_dir = os.path.join(os.path.dirname(__file__), "testdata")
    filepath = os.path.join(test_dir, filename)
    source = read_file(filepath)

    output = lex(source)
    assert output == tokens


# TODO: add lots of failing tests, with proper error message location, etc.
