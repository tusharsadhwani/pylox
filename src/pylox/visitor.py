from __future__ import annotations

from typing import Callable, Generic, TypeVar, overload

from pylox.nodes import Expr, Program

T = TypeVar("T")


class Visitor(Generic[T]):
    """A pythonic visitor class. Needs no boilerplate."""

    @overload
    def visit(self, node: Expr) -> T:
        ...

    @overload
    def visit(self, node: Program) -> None:
        ...

    def visit(self, node: Expr | Program) -> T | None:
        if isinstance(node, Program):
            for stmt in node.body:
                visitor_name = "visit_" + stmt.__class__.__name__
                visitor: Callable[..., T] = getattr(self, visitor_name)
                visitor(stmt)

            return None

        visitor_name = "visit_" + node.__class__.__name__
        visitor = getattr(self, visitor_name)
        return visitor(node)
