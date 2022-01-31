from __future__ import annotations

from attr import define, field

from pylox.tokens import Token


@define(kw_only=True)
class Node:
    index: int = field(default=-1, repr=False)


@define
class Expr(Node):
    ...


@define
class Literal(Expr):
    value: object


@define
class Variable(Expr):
    name: Token


@define
class Assignment(Expr):
    name: Token
    value: Expr


@define
class Unary(Expr):
    operator: Token
    right: Expr


@define
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@define
class Grouping(Expr):
    expression: Expr


@define
class Stmt(Node):
    ...


@define
class Declaration(Stmt):
    ...


@define
class VarDeclaration(Declaration):
    name: Token
    initializer: Expr | None = None


@define
class Block(Stmt):
    body: list[Stmt]


@define
class Print(Stmt):
    value: Expr


@define
class If(Stmt):
    condition: Expr
    body: Stmt
    else_body: Stmt | None = None


@define
class While(Stmt):
    condition: Expr
    body: Stmt


@define
class For(Stmt):
    initializer: VarDeclaration | Stmt | None
    condition: Expr | None
    increment: Expr | None
    body: Stmt


@define
class ExprStmt(Stmt):
    expression: Expr


@define
class Program(Node):
    body: list[Stmt]
