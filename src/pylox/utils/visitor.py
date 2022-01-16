from typing import Callable, Generic, TypeVar

from pylox.expr import Expr

T = TypeVar("T")


class Visitor(Generic[T]):
    """A pythonic visitor class. Needs no boilerplate."""

    def visit(self, node: Expr) -> T:
        visitor_name = "visit_" + node.__class__.__name__
        visitor: Callable[..., T] = getattr(self, visitor_name)
        return visitor(node)
