from __future__ import annotations

from typing import Callable, Generic, TypeVar

from pylox.nodes import Node

T = TypeVar("T")


class Visitor(Generic[T]):
    """A pythonic visitor class. Needs no boilerplate."""

    def generic_visit(self, node: Node) -> T:
        visitor_name = "visit_" + node.__class__.__name__
        visitor: Callable[..., T] = getattr(self, visitor_name)
        return visitor(node)
