from dataclasses import dataclass

from .tokens import Token


@dataclass
class Expr:
    ...


@dataclass
class Literal(Expr):
    value: object


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Grouping(Expr):
    expression: Expr
