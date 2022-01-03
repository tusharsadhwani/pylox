from enum import Enum, unique
from typing import NamedTuple, Optional


class ParseError(Exception):
    ...


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


class Token(NamedTuple):
    token_type: TokenType
    source: str
    value: Optional[object] = None
    # TODO: add location information


def scan_comment(source: str, index: int) -> int:
    char = source[index]
    index += 1

    while char != "\n":
        char = source[index]
        index += 1

    return index


def scan_string(source: str, index: int) -> tuple[Token, int]:
    # TODO: single quote support
    string = ""

    char = source[index]
    index += 1

    while char != '"':
        string += char
        char = source[index]
        index += 1

    source = f'"{string}"'
    token = Token(TokenType.STRING, source, string)
    return token, index


def scan_number(source: str, index: int, digit: str) -> tuple[Token, int]:
    decimal_seen = False

    number = digit
    digit = source[index]
    while digit.isdigit() or (not decimal_seen and digit == "."):
        index += 1

        if digit == ".":
            decimal_seen = True

        number += digit

        digit = source[index]

    token = Token(TokenType.NUMBER, number, float(number))
    return token, index


def scan_identifier(source: str, index: int, char: str) -> tuple[Token, int]:
    identifier = char

    char = source[index]
    while char.isalnum() or char == "_":
        index += 1

        identifier += char
        char = source[index]

    if identifier in KEYWORD_TOKENS:
        token_type = KEYWORD_TOKENS[identifier]
        token = Token(token_type, identifier)
    else:
        token = Token(TokenType.IDENTIFIER, identifier)
    return token, index


def lex(source: str) -> list[Token]:
    tokens: list[Token] = []

    index = 0
    while index < len(source):
        char = source[index]
        # index will always point at the next character to read.
        index += 1

        if char in (" ", "\t", "\r", "\n"):
            pass

        elif char == "(":
            tokens.append(Token(TokenType.LEFT_PAREN, char))
        elif char == ")":
            tokens.append(Token(TokenType.RIGHT_PAREN, char))
        elif char == "{":
            tokens.append(Token(TokenType.LEFT_BRACE, char))
        elif char == "}":
            tokens.append(Token(TokenType.RIGHT_BRACE, char))
        elif char == ",":
            tokens.append(Token(TokenType.COMMA, char))
        elif char == ".":
            tokens.append(Token(TokenType.DOT, char))
        elif char == ";":
            tokens.append(Token(TokenType.SEMICOLON, char))
        elif char == "+":
            tokens.append(Token(TokenType.PLUS, char))
        elif char == "-":
            tokens.append(Token(TokenType.MINUS, char))
        elif char == "*":
            tokens.append(Token(TokenType.STAR, char))
        elif char == "%":
            tokens.append(Token(TokenType.PERCENT, char))

        elif char == "/":
            next_char = source[index]
            if next_char == "/":
                index = scan_comment(source, index)
            else:
                tokens.append(Token(TokenType.SLASH, char))

        elif char == "=":
            next_char = source[index]
            if next_char == "=":
                index += 1
                tokens.append(Token(TokenType.EQUAL_EQUAL, "=="))
            else:
                tokens.append(Token(TokenType.EQUAL, char))

        elif char == "!":
            next_char = source[index]
            if next_char == "=":
                index += 1
                tokens.append(Token(TokenType.BANG_EQUAL, "!="))
            else:
                tokens.append(Token(TokenType.BANG, char))

        elif char == "<":
            next_char = source[index]
            if next_char == "=":
                index += 1
                tokens.append(Token(TokenType.LESS_EQUAL, "<="))
            else:
                tokens.append(Token(TokenType.LESS, char))

        elif char == ">":
            next_char = source[index]
            if next_char == "=":
                index += 1
                tokens.append(Token(TokenType.GREATER_EQUAL, ">="))
            else:
                tokens.append(Token(TokenType.GREATER, char))

        elif char == '"':
            token, index = scan_string(source, index)
            tokens.append(token)

        elif char.isdigit():
            token, index = scan_number(source, index, char)
            tokens.append(token)

        elif char.isalpha() or char == "_":
            token, index = scan_identifier(source, index, char)
            tokens.append(token)

        else:
            raise ParseError(f"Unknown character found: {char}")

    tokens.append(Token(TokenType.EOF, "", None))
    return tokens


def parse(source: str) -> None:
    tokens = lex(source)
    # TODO: parse
