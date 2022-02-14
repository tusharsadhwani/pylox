from __future__ import annotations

from collections import UserList
from contextlib import contextmanager
from enum import Enum, unique
from typing import Generator, Iterator, Sequence, TypeVar

from pylox.interpreter import Interpreter
from pylox.nodes import (
    Assignment,
    Binary,
    Block,
    Call,
    Expr,
    ExprStmt,
    For,
    FunctionDef,
    Grouping,
    If,
    Literal,
    Print,
    Program,
    ReturnStmt,
    Stmt,
    Unary,
    VarDeclaration,
    Variable,
    While,
)
from pylox.parser import ParseError
from pylox.tokens import Token
from pylox.visitor import Visitor


@unique
class ScopeType(Enum):
    GLOBAL = "global"
    BLOCK = "block"
    FUNCTION = "function"


T = TypeVar("T")


class Stack(UserList[T]):
    def __repr__(self) -> str:
        return f"Stack({self.data!r})"

    def __iter__(self) -> Iterator[T]:
        for i in range(len(self) - 1, -1, -1):
            yield self[i]


class Resolver(Visitor[None]):
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        self.scope_stack: Stack[set[str]] = Stack()
        self.current_scope = ScopeType.GLOBAL

    @contextmanager
    def new_scope(self, scope_type: ScopeType) -> Generator[None, None, None]:
        old_scope = self.current_scope

        self.current_scope = scope_type
        self.scope_stack.append(set())
        yield
        self.scope_stack.pop()

        self.current_scope = old_scope

    def peek(self) -> set[str]:
        return self.scope_stack[-1]

    def define(self, name: Token) -> None:
        # Don't define anything for globals
        if self.current_scope == ScopeType.GLOBAL:
            return

        var_name = name.string
        scope = self.peek()
        if var_name in scope:
            raise ParseError(
                f"Variable {var_name!r} already defined in this scope", name
            )
        scope.add(var_name)

    def visit(self, program: Program) -> None:
        self.resolve(program.body)

    def resolve(self, item: Expr | Stmt | Sequence[Stmt]) -> None:
        if isinstance(item, Sequence):
            for stmt in item:
                self.resolve(stmt)
        else:
            self.generic_visit(item)

    def resolve_local(self, expr: Expr, name: str) -> None:
        for depth, scope in enumerate(self.scope_stack):
            if name in scope:
                self.interpreter.resolve(expr, depth)
                return

    def visit_Block(self, block: Block) -> None:
        with self.new_scope(ScopeType.BLOCK):
            self.resolve(block.body)

    def visit_VarDeclaration(self, var_decl: VarDeclaration) -> None:
        if var_decl.initializer is not None:
            self.resolve(var_decl.initializer)

        self.define(var_decl.name)

    def visit_FunctionDef(self, function_def: FunctionDef) -> None:
        self.define(function_def.name)
        with self.new_scope(ScopeType.FUNCTION):
            for parameter in function_def.parameters:
                self.define(parameter)

            self.resolve(function_def.body)

    def visit_Variable(self, variable: Variable) -> None:
        self.resolve_local(variable, name=variable.name.string)

    def visit_Assignment(self, assignment: Assignment) -> None:
        self.resolve(assignment.value)
        self.resolve_local(assignment, name=assignment.name.string)

    def visit_Unary(self, unary: Unary) -> None:
        self.resolve(unary.right)

    def visit_Binary(self, binary: Binary) -> None:
        self.resolve(binary.left)
        self.resolve(binary.right)

    def visit_Grouping(self, grouping: Grouping) -> None:
        self.resolve(grouping.expression)

    def visit_If(self, if_stmt: If) -> None:
        self.resolve(if_stmt.condition)
        self.resolve(if_stmt.body)
        if if_stmt.else_body is not None:
            self.resolve(if_stmt.else_body)

    def visit_While(self, while_stmt: While) -> None:
        self.resolve(while_stmt.condition)
        self.resolve(while_stmt.body)

    def visit_For(self, for_stmt: For) -> None:
        if for_stmt.initializer is not None:
            self.resolve(for_stmt.initializer)
        if for_stmt.condition is not None:
            self.resolve(for_stmt.condition)
        if for_stmt.increment is not None:
            self.resolve(for_stmt.increment)

        self.resolve(for_stmt.body)

    def visit_Call(self, call: Call) -> None:
        self.resolve(call.callee)

        for argument in call.arguments:
            self.resolve(argument)

    def visit_Print(self, print_stmt: Print) -> None:
        self.resolve(print_stmt.value)

    def visit_ReturnStmt(self, return_stmt: ReturnStmt) -> None:
        if self.current_scope != ScopeType.FUNCTION:
            raise ParseError("Cannot return outside of a function", return_stmt.keyword)

        if return_stmt.value is not None:
            self.resolve(return_stmt.value)

    def visit_ExprStmt(self, expr_stmt: ExprStmt) -> None:
        self.resolve(expr_stmt.expression)

    def visit_Literal(self, _: Literal) -> None:
        """Nothing to do here."""
