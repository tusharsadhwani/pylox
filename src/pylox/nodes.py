from __future__ import annotations

from dataclasses import dataclass

from pylox.tokens import Token


@dataclass
class Expr:
    ...


@dataclass
class Literal(Expr):
    value: object


@dataclass
class Variable(Expr):
    name: Token


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


@dataclass
class Stmt:
    ...


@dataclass
class Declaration(Stmt):
    ...


@dataclass
class VarDeclaration(Declaration):
    name: Token
    initializer: Expr | None = None


@dataclass
class Print(Stmt):
    value: Expr


@dataclass
class ExprStmt(Stmt):
    expression: Expr


@dataclass
class Program:
    body: list[Stmt]
