from pylox.expr import Expr


class Visitor:
    """A pythonic visitor class. Needs no boilerplate."""

    def visit(self, node: Expr) -> object:
        visitor_name = "visit_" + node.__class__.__name__
        visitor = getattr(self, visitor_name)
        return visitor(node)
