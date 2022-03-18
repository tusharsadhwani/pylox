from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique

from pylox.lox_types import LoxType


@unique
class TokenType(Enum):
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    DOT = "."
    SEMICOLON = ";"

    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"

    EQUAL = "="
    EQUAL_EQUAL = "=="
    BANG = "!"
    BANG_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="

    VAR = "var"
    TRUE = "true"
    FALSE = "false"
    NIL = "nil"
    PRINT = "print"
    AND = "and"
    OR = "or"
    IF = "if"
    ELSE = "else"
    FOR = "for"
    WHILE = "while"
    FUN = "fun"
    RETURN = "return"
    CLASS = "class"
    THIS = "this"
    SUPER = "super"

    IDENTIFIER = "Identifier"
    STRING = "String"
    NUMBER = "Number"

    EOF = "EOF"


KEYWORD_TOKENS = {
    "var": TokenType.VAR,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "nil": TokenType.NIL,
    "print": TokenType.PRINT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "fun": TokenType.FUN,
    "return": TokenType.RETURN,
    "class": TokenType.CLASS,
    "this": TokenType.THIS,
    "super": TokenType.SUPER,
}


@dataclass(frozen=True)
class Token:
    token_type: TokenType
    string: str
    value: LoxType | None = None
    index: int = -1

    def __repr__(self) -> str:  # pragma: no cover
        if self.value is None:
            return f"Token({self.token_type}, {self.string!r}, index={self.index})"

        return (
            f"Token({self.token_type}, {self.string!r}, {self.value!r}, "
            f"index={self.index})"
        )


EOF = Token(TokenType.EOF, "")
