from __future__ import annotations

from contextlib import contextmanager
from enum import Enum, unique
from typing import Iterator, List, Sequence, TypeVar

from pylox.interpreter import Interpreter
from pylox.nodes import (
    Assignment,
    Block,
    ClassDef,
    Expr,
    FunctionDef,
    Node,
    Program,
    ReturnStmt,
    Super,
    This,
    VarDeclaration,
    Variable,
)
from pylox.parser import ParseError
from pylox.tokens import Token
from pylox.utils import iter_children
from pylox.visitor import Visitor


@unique
class ScopeType(Enum):
    GLOBAL = "global"
    BLOCK = "block"
    FUNCTION = "function"
    CLASS = "class"
    SUBCLASS = "subclass"


T = TypeVar("T")


class Stack(List[T]):
    def __repr__(self) -> str:  # pragma: no cover -- internal only
        return f"Stack({super().__repr__()})"

    def __iter__(self) -> Iterator[T]:
        for i in range(len(self) - 1, -1, -1):
            yield self[i]


class Resolver(Visitor[None]):
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        self.scope_stack: Stack[set[str]] = Stack()
        self.current_scope = ScopeType.GLOBAL
        self.function_scope = ScopeType.GLOBAL
        self.class_scope = ScopeType.GLOBAL

    @contextmanager
    def new_scope(self, scope_type: ScopeType = ScopeType.BLOCK) -> Iterator[None]:
        old_scope = self.current_scope

        self.current_scope = scope_type
        if scope_type == ScopeType.FUNCTION:
            self.function_scope = scope_type
        elif scope_type in (ScopeType.CLASS, ScopeType.SUBCLASS):
            self.class_scope = scope_type

        self.scope_stack.append(set())
        yield
        self.scope_stack.pop()

        self.current_scope = old_scope
        if scope_type == ScopeType.FUNCTION:
            self.function_scope = old_scope
        elif scope_type in (ScopeType.CLASS, ScopeType.SUBCLASS):
            self.class_scope = old_scope

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

    def resolve(self, item: Node | Sequence[Node]) -> None:
        if isinstance(item, Sequence):
            for stmt in item:
                self.resolve(stmt)
        else:
            visitor = self.get_visitor(item)
            if visitor is not None:
                visitor(item)
            else:
                # If there's no special visitor, resolve all children
                for child in iter_children(item):
                    self.resolve(child)

    def resolve_local(self, expr: Expr, name: str) -> None:
        for depth, scope in enumerate(self.scope_stack):
            if name in scope:
                self.interpreter.resolve(expr, depth)
                return

    def visit_Block(self, block: Block) -> None:
        with self.new_scope():
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

    def visit_ClassDef(self, class_def: ClassDef) -> None:
        self.define(class_def.name)

        # Edge case: Trying to inherit a class from itself
        if (
            class_def.superclass is not None
            and class_def.name.string == class_def.superclass.name.string
        ):
            raise ParseError("A class cannot inherit from itself", class_def.name)

        with self.new_scope():
            if class_def.superclass is not None:
                scope = self.peek()
                scope.add("super")

            scope_type = ScopeType.SUBCLASS if class_def.superclass else ScopeType.CLASS
            with self.new_scope(scope_type):
                scope = self.peek()
                scope.add("this")

                for method in class_def.methods:
                    self.define(method.name)
                    with self.new_scope(ScopeType.FUNCTION):
                        for parameter in method.parameters:
                            self.define(parameter)

                        self.resolve(method.body)

    def visit_Variable(self, variable: Variable) -> None:
        self.resolve_local(variable, name=variable.name.string)

    def visit_Assignment(self, assignment: Assignment) -> None:
        self.resolve(assignment.value)
        self.resolve_local(assignment, name=assignment.name.string)

    def visit_ReturnStmt(self, return_stmt: ReturnStmt) -> None:
        if self.function_scope != ScopeType.FUNCTION:
            raise ParseError("Cannot return outside of a function", return_stmt.keyword)

        if return_stmt.value is not None:
            self.resolve(return_stmt.value)

    def visit_This(self, this: This) -> None:
        if self.class_scope != ScopeType.CLASS:
            raise ParseError("Cannot use 'this' outside of a class", this.keyword)

        self.resolve_local(this, this.keyword.string)

    def visit_Super(self, super: Super) -> None:
        if self.class_scope == ScopeType.CLASS:
            raise ParseError(
                "Cannot use 'super' in a class with no superclass",
                super.keyword,
            )

        if self.class_scope != ScopeType.SUBCLASS:
            raise ParseError("Cannot use 'super' outside of a class", super.keyword)

        self.resolve_local(super, super.keyword.string)
