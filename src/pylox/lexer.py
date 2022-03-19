from __future__ import annotations

import sys

from pylox.errors import LoxError
from pylox.lox_types import LoxType, Number
from pylox.tokens import EOF, KEYWORD_TOKENS, Token, TokenType


class LexError(LoxError):
    ...


class LexIncompleteError(Exception):
    ...


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

    def add_token(self, token_type: TokenType, value: LoxType = None) -> None:
        """Adds a new token for the just-scanned characters."""
        string = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, string, value, self.start))
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

        elif char in ('"', "'"):
            self.scan_string(char)

        elif char.isdigit():
            self.scan_number()

        elif char.isalpha() or char == "_":
            self.scan_identifier()

        else:
            raise LexError(f"Unknown character found: '{char}'", self.start)

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

    def scan_string(self, quote_char: str) -> None:
        unescaped_chars = []
        while not self.scanned:
            char = self.peek()
            self.advance()

            if char == quote_char:
                break

            if char != "\\":
                unescaped_chars.append(char)
                continue

            # Escaping the next character
            next_char = self.peek()
            if next_char == "":
                # Happens in interactive mode, when writing multiline
                # strings. Treat it as EOF.
                raise LexIncompleteError  # pragma: no cover -- not sure how to test

            if next_char == "\n":
                pass  # trailing backslash means ignore the newline
            elif next_char == "\\":
                unescaped_chars.append("\\")
            elif next_char == "n":
                unescaped_chars.append("\n")
            elif next_char == "t":
                unescaped_chars.append("\t")
            elif next_char == "'":
                unescaped_chars.append("'")
            elif next_char == '"':
                unescaped_chars.append('"')
            else:
                escape = char + next_char
                raise LexError(
                    f"Unknown escape sequence: '{escape}'",
                    index=self.current,
                )

            self.advance()
        else:
            # No end quote found, so no break
            raise LexError("Unterminated string", self.start)

        string = "".join(unescaped_chars)
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

        number = Number(self.source[self.start : self.current])
        self.add_token(TokenType.NUMBER, number)


if __name__ == "__main__":
    _source = " ".join(sys.argv[1:])
    print(Lexer(_source).tokens)
