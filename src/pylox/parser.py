from enum import Enum, unique
from typing import NamedTuple, Optional


class ParseError(Exception):
    ...


class LexError(ParseError):
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
    string: str
    value: Optional[object] = None
    # TODO: add location information


EOF = Token(TokenType.EOF, "")


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: list[Token] = []
        # Start and current represent the two ends of the current token
        self.start = self.current = 0

        self.scan_tokens()

    @property
    def scanned(self) -> int:
        """Returns True if the source has been fully scanned."""
        return self.current >= len(self.source)

    def advance(self) -> None:
        """Advance the current pointer."""
        self.current += 1

    def peek(self) -> str:
        """Returns the current character, without actually consuming it."""
        if self.scanned:
            return ""

        return self.source[self.current]

    def peek_next(self) -> str:
        """Returns the next character, without actually consuming it."""
        if self.current + 1 >= len(self.source):
            return ""

        return self.source[self.current + 1]

    def read_char(self) -> str:
        """
        Reads one character from the source.
        If the source has been exhausted, returns an empty string.
        """
        if self.scanned:
            return ""

        char = self.source[self.current]
        # current will always point at the next character to read.
        self.advance()

        return char

    def match_next(self, char: str) -> bool:
        """
        Returns True and reads one character from source, but only if it
        matches the given character. Returns False otherwise.
        """
        if self.scanned:
            return False

        if self.source[self.current] == char:
            self.advance()
            return True

        return False

    def add_token(self, token_type: TokenType, value: object = None) -> None:
        """Adds a new token for the just-scanned characters."""
        string = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, string, value))
        self.start = self.current

    def scan_tokens(self) -> list[Token]:
        """Scans the source to produce tokens of variables, operators, strings etc."""
        while not self.scanned:
            self.scan_token()

        self.tokens.append(EOF)
        return self.tokens

    def scan_token(self) -> None:
        char = self.read_char()

        if char in (" ", "\t", "\r", "\n"):
            # Ignore whitespace
            self.start += 1

        elif char == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif char == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif char == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif char == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif char == ",":
            self.add_token(TokenType.COMMA)
        elif char == ".":
            self.add_token(TokenType.DOT)
        elif char == ";":
            self.add_token(TokenType.SEMICOLON)
        elif char == "+":
            self.add_token(TokenType.PLUS)
        elif char == "-":
            self.add_token(TokenType.MINUS)
        elif char == "*":
            self.add_token(TokenType.STAR)
        elif char == "%":
            self.add_token(TokenType.PERCENT)

        elif char == "/":
            if self.match_next("/"):
                self.scan_comment()
            else:
                self.add_token(TokenType.SLASH)

        elif char == "=":
            if self.match_next("="):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)

        elif char == "!":
            if self.match_next("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG)

        elif char == "<":
            if self.match_next("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)

        elif char == ">":
            if self.match_next("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)

        elif char == '"':
            self.scan_string()

        elif char.isdigit():
            self.scan_number()

        elif char.isalpha() or char == "_":
            self.scan_identifier()

        else:
            raise LexError(f"Unknown character found: {char}")

    def scan_comment(self) -> None:
        """Reads and discards a comment. A comment goes on till a newline."""
        while not self.scanned and self.peek() != "\n":
            self.advance()

        # Since comments are thrown away, reset the start pointer
        self.start = self.current

    def scan_identifier(self) -> None:
        """Scans keywords and variable names."""
        while not self.scanned and (self.peek().isalnum() or self.peek() == "_"):
            self.advance()

        identifier = self.source[self.start : self.current]

        if identifier in KEYWORD_TOKENS:
            token_type = KEYWORD_TOKENS[identifier]
            self.add_token(token_type)
        else:
            self.add_token(TokenType.IDENTIFIER)

    def scan_string(self) -> None:
        # TODO: single quote support
        while not self.scanned and self.peek() != '"':
            self.advance()

        if self.scanned:
            # TODO: better error handling
            raise LexError("Unterminated string")

        string = self.source[self.start + 1 : self.current]

        # Advance past the closing quote
        self.advance()

        self.add_token(TokenType.STRING, string)

    def scan_number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        # decimal support
        if self.peek() == ".":
            if self.peek_next().isdigit():
                self.advance()
                while self.peek().isdigit():
                    self.advance()

        number = float(self.source[self.start : self.current])
        self.add_token(TokenType.NUMBER, number)
