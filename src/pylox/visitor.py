from __future__ import annotations

from typing import Callable, Generic, TypeVar, overload

from pylox.nodes import Block, Expr, Node, Program, Stmt

T = TypeVar("T")


class Visitor(Generic[T]):
    """A pythonic visitor class. Needs no boilerplate."""

    @overload
    def visit(self, node: Expr) -> T:
        ...

    @overload
    def visit(self, node: Program | Block) -> None:
        ...

    def visit(self, node: Expr | Program | Block) -> T | None:
        if isinstance(node, (Program, Block)):
            for stmt in node.body:
                self.visit_Stmt(stmt)

            return None

        return self.visit_Expr(node)

    def visit_Node(self, node: Node) -> T:
        visitor_name = "visit_" + node.__class__.__name__
        visitor: Callable[..., T] = getattr(self, visitor_name)
        return visitor(node)

    def visit_Stmt(self, stmt: Stmt) -> None:
        self.visit_Node(stmt)

    def visit_Expr(self, expr: Expr) -> T:
        return self.visit_Node(expr)
