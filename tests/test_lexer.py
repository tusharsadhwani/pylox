from __future__ import annotations

import os.path

import pytest

from pylox.lexer import Lexer, LexError
from pylox.tokens import EOF, Token, TokenType


def read_file(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


@pytest.mark.parametrize(
    ("code", "tokens"),
    (
        ("", [EOF]),
        ("abc", [Token(TokenType.IDENTIFIER, "abc", index=0), EOF]),
        ("nil", [Token(TokenType.NIL, "nil", index=0), EOF]),
        ("12", [Token(TokenType.INTEGER, "12", 12, index=0), EOF]),
        (
            "2.",
            [
                Token(TokenType.INTEGER, "2", 2, index=0),
                Token(TokenType.DOT, ".", index=1),
                EOF,
            ],
        ),
        (
            '"abc\n123"',
            [Token(TokenType.STRING, '"abc\n123"', "abc\n123", index=0), EOF],
        ),
        (
            "a=1",
            [
                Token(TokenType.IDENTIFIER, "a", index=0),
                Token(TokenType.EQUAL, "=", index=1),
                Token(TokenType.INTEGER, "1", 1, index=2),
                EOF,
            ],
        ),
        (
            "print a.b == c",
            [
                Token(TokenType.PRINT, "print", index=0),
                Token(TokenType.IDENTIFIER, "a", index=6),
                Token(TokenType.DOT, ".", index=7),
                Token(TokenType.IDENTIFIER, "b", index=8),
                Token(TokenType.EQUAL_EQUAL, "==", index=10),
                Token(TokenType.IDENTIFIER, "c", index=13),
                EOF,
            ],
        ),
        (
            "f(x, y)",
            [
                Token(TokenType.IDENTIFIER, "f", index=0),
                Token(TokenType.LEFT_PAREN, "(", index=1),
                Token(TokenType.IDENTIFIER, "x", index=2),
                Token(TokenType.COMMA, ",", index=3),
                Token(TokenType.IDENTIFIER, "y", index=5),
                Token(TokenType.RIGHT_PAREN, ")", index=6),
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
                Token(TokenType.PRINT, "print", index=0),
                Token(TokenType.STRING, "'Hello'", "Hello", index=6),
                Token(TokenType.SEMICOLON, ";", index=13),
                Token(TokenType.VAR, "var", index=15),
                Token(TokenType.IDENTIFIER, "a", index=19),
                Token(TokenType.EQUAL, "=", index=21),
                Token(TokenType.INTEGER, "5", 5, index=23),
                Token(TokenType.SEMICOLON, ";", index=24),
                Token(TokenType.PRINT, "print", index=26),
                Token(TokenType.IDENTIFIER, "a", index=32),
                Token(TokenType.SEMICOLON, ";", index=33),
                Token(TokenType.VAR, "var", index=35),
                Token(TokenType.IDENTIFIER, "a", index=39),
                Token(TokenType.EQUAL, "=", index=41),
                Token(TokenType.FALSE, "false", index=43),
                Token(TokenType.SEMICOLON, ";", index=48),
                Token(TokenType.PRINT, "print", index=50),
                Token(TokenType.IDENTIFIER, "a", index=56),
                Token(TokenType.SEMICOLON, ";", index=57),
                Token(TokenType.PRINT, "print", index=59),
                Token(TokenType.LEFT_PAREN, "(", index=65),
                Token(TokenType.FLOAT, "6.75", 6.75, index=66),
                Token(TokenType.STAR, "*", index=71),
                Token(TokenType.LEFT_PAREN, "(", index=73),
                Token(TokenType.INTEGER, "3", 3, index=74),
                Token(TokenType.PLUS, "+", index=76),
                Token(TokenType.INTEGER, "5", 5, index=78),
                Token(TokenType.RIGHT_PAREN, ")", index=79),
                Token(TokenType.SLASH, "/", index=81),
                Token(TokenType.INTEGER, "2", 2, index=83),
                Token(TokenType.RIGHT_PAREN, ")", index=84),
                Token(TokenType.SEMICOLON, ";", index=85),
                EOF,
            ],
        ),
        (
            "fibonacci.lox",
            [
                Token(TokenType.VAR, "var", index=0),
                Token(TokenType.IDENTIFIER, "a", index=4),
                Token(TokenType.EQUAL, "=", index=6),
                Token(TokenType.INTEGER, "0", 0, index=8),
                Token(TokenType.SEMICOLON, ";", index=9),
                Token(TokenType.VAR, "var", index=11),
                Token(TokenType.IDENTIFIER, "b", index=15),
                Token(TokenType.EQUAL, "=", index=17),
                Token(TokenType.INTEGER, "1", 1, index=19),
                Token(TokenType.SEMICOLON, ";", index=20),
                Token(TokenType.WHILE, "while", index=23),
                Token(TokenType.LEFT_PAREN, "(", index=29),
                Token(TokenType.IDENTIFIER, "a", index=30),
                Token(TokenType.LESS, "<", index=32),
                Token(TokenType.INTEGER, "10000", 10000, index=34),
                Token(TokenType.RIGHT_PAREN, ")", index=39),
                Token(TokenType.LEFT_BRACE, "{", index=41),
                Token(TokenType.PRINT, "print", index=85),
                Token(TokenType.IDENTIFIER, "a", index=91),
                Token(TokenType.SEMICOLON, ";", index=92),
                Token(TokenType.VAR, "var", index=96),
                Token(TokenType.IDENTIFIER, "temp", index=100),
                Token(TokenType.EQUAL, "=", index=105),
                Token(TokenType.IDENTIFIER, "a", index=107),
                Token(TokenType.SEMICOLON, ";", index=108),
                Token(TokenType.IDENTIFIER, "a", index=112),
                Token(TokenType.EQUAL, "=", index=114),
                Token(TokenType.IDENTIFIER, "b", index=116),
                Token(TokenType.SEMICOLON, ";", index=117),
                Token(TokenType.IDENTIFIER, "b", index=121),
                Token(TokenType.EQUAL, "=", index=123),
                Token(TokenType.IDENTIFIER, "temp", index=125),
                Token(TokenType.PLUS, "+", index=130),
                Token(TokenType.IDENTIFIER, "b", index=132),
                Token(TokenType.SEMICOLON, ";", index=133),
                Token(TokenType.RIGHT_BRACE, "}", index=135),
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


@pytest.mark.parametrize(
    ("code", "error_msg"),
    (
        ("#", "Unknown character found: '#'"),
        ('string = "abc', "Unterminated string"),
    ),
)
def test_lex_fail(code: str, error_msg: str) -> None:
    with pytest.raises(LexError) as exc:
        Lexer(code).tokens

    assert exc.value.args[0] == error_msg
