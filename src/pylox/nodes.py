from __future__ import annotations

from typing import Sequence

from attr import define, field

from pylox.lox_types import LoxType
from pylox.tokens import Token


@define(kw_only=True, frozen=True)
class Node:
    index: int = field(default=-1, repr=False)


@define
class Expr(Node):
    ...


@define
class Literal(Expr):
    value: LoxType


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
class Call(Expr):
    callee: Expr
    paren: Token  # to store the location of the bracket, for error reporting
    arguments: Sequence[Expr] = ()


@define
class Get(Expr):
    object: Expr
    name: Token


@define
class Set(Expr):
    object: Expr
    name: Token
    value: Expr


@define
class This(Expr):
    keyword: Token


@define
class Super(Expr):
    keyword: Token
    method: Variable


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
class FunctionDef(Declaration):
    name: Token
    parameters: Sequence[Token]
    body: Sequence[Stmt]


@define
class ClassDef(Declaration):
    name: Token
    superclass: Variable | None
    methods: Sequence[FunctionDef]


@define
class Block(Stmt):
    body: Sequence[Stmt]


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
class ReturnStmt(Stmt):
    keyword: Token
    value: Expr | None = None


@define
class ExprStmt(Stmt):
    expression: Expr


@define
class Program(Node):
    body: Sequence[Stmt]
