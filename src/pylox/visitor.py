from __future__ import annotations

from typing import Callable, Generic, TypeVar

from pylox.nodes import Node

T = TypeVar("T")


class Visitor(Generic[T]):
    """A pythonic visitor class. Needs no boilerplate."""

    def get_visitor(self, node: Node) -> Callable[..., T]:
        visitor_name = "visit_" + node.__class__.__name__
        visitor: Callable[..., T] = getattr(self, visitor_name, None)
        return visitor

    def generic_visit(self, node: Node) -> T:
        visitor = self.get_visitor(node)
        if visitor is None:  # pragma: no cover
            raise NotImplementedError(f"Visitor for {node!r} not defined")

        return visitor(node)
