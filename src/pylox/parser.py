from __future__ import annotations

from pylox.expr import Binary, Expr, Grouping, Literal, Unary
from pylox.tokens import EOF, Token, TokenType


class ParseError(Exception):
    ...


class Parser:
    """
    Current grammar:
        program -> expression
        expression -> equality
        equality -> comparison (("==" | "!=") comparison)*
        comparison -> term ((">" | ">=" | "<" | "<=") term)*
        term -> factor (("+" / "-") factor)*
        factor -> unary (("*" / "/") unary)*
        unary -> ("-" | "!") unary | primary
        primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")"
    """

    def __init__(self, tokens: list[Token]) -> None:
        if tokens[-1] != EOF:
            raise ValueError(f"Expected EOF as the last token, found {tokens[-1]}")
        self.tokens = tokens
        self.index = 0

    @property
    def scanned(self) -> int:
        """Returns True if tokens has been fully scanned."""
        if self.index >= len(self.tokens) - 1:
            return True

        return False

    def get_token(self) -> Token | None:
        if self.scanned:
            return None

        return self.tokens[self.index]

    def match_next(self, *token_types: TokenType) -> bool:
        token = self.get_token()

        if token is None:
            return False

        if token.token_type in token_types:
            self.index += 1
            return True

        return False

    def previous(self) -> Token:
        if self.index == 0:
            raise RuntimeError("previous() ran at beginning of file")

        return self.tokens[self.index - 1]

    def parse(self) -> Expr:
        return self.parse_expression()

    def parse_expression(self) -> Expr:
        if self.scanned:
            return Expr()

        return self.parse_equality()

    def parse_equality(self) -> Expr:
        left = self.parse_comparison()

        while self.match_next(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.parse_comparison()

            left = Binary(left, operator, right)

        return left

    def parse_comparison(self) -> Expr:
        left = self.parse_term()

        while self.match_next(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.parse_term()

            left = Binary(left, operator, right)

        return left

    def parse_term(self) -> Expr:
        left = self.parse_factor()

        while self.match_next(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.parse_factor()

            left = Binary(left, operator, right)

        return left

    def parse_factor(self) -> Expr:
        left = self.parse_unary()

        while self.match_next(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.parse_unary()

            left = Binary(left, operator, right)

        return left

    def parse_unary(self) -> Expr:
        if self.match_next(TokenType.MINUS, TokenType.BANG):
            operator = self.previous()
            right = self.parse_primary()
            return Unary(operator, right)

        return self.parse_primary()

    def parse_primary(self) -> Expr:
        if self.match_next(TokenType.IDENTIFIER):
            token = self.previous()
            return Literal(token.string)

        if self.match_next(TokenType.STRING, TokenType.NUMBER):
            token = self.previous()
            return Literal(token.value)

        if self.match_next(TokenType.TRUE):
            return Literal(True)
        if self.match_next(TokenType.FALSE):
            return Literal(False)
        if self.match_next(TokenType.NIL):
            return Literal(None)

        if self.match_next(TokenType.LEFT_PAREN):
            expression = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN)
            return Grouping(expression)

        raise NotImplementedError  # TODO: exception handling

    def consume(self, expected_type: TokenType) -> None:
        """Consumes one token. If it's not of the expected type, throws."""
        token = self.get_token()

        if token is None:
            raise ParseError(f"Expected to find {expected_type.value!r}, found EOF")

        if token.token_type != expected_type:
            raise ParseError(
                f"Expected to find {expected_type.value!r}, found {token.string!r}"
            )

        self.index += 1
