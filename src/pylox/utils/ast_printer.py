from __future__ import annotations

from pylox.lexer import Lexer
from pylox.nodes import Binary, Call, Expr, ExprStmt, Grouping, Literal, Unary, Variable
from pylox.parser import Parser
from pylox.visitor import Visitor


class AstPrinter(Visitor[str]):
    # TODO: Find a way for mypy to enforce every visit function's
    # return value to be str.

    def visit(self, expr: Expr) -> str:
        return self.generic_visit(expr)

    @staticmethod
    def visit_Literal(literal: Literal) -> str:
        if literal.value is None:
            return "nil"

        if isinstance(literal.value, bool):
            return f"{literal.value}".lower()

        return f"{literal.value!r}"

    @staticmethod
    def visit_Variable(variable: Variable) -> str:
        return variable.name.string

    def visit_Unary(self, unary: Unary) -> str:
        return f"({unary.operator.string} {self.visit(unary.right)})"

    def visit_Binary(self, binary: Binary) -> str:
        return (
            f"({self.visit(binary.left)} "
            f"{binary.operator.string} "
            f"{self.visit(binary.right)})"
        )

    def visit_Grouping(self, grouping: Grouping) -> str:
        return f"(group {self.visit(grouping.expression)})"

    def visit_Call(self, call: Call) -> str:
        return (
            f"({self.visit(call.callee)} "
            f"{' '.join(self.visit(arg) for arg in call.arguments)})"
        )


if __name__ == "__main__":
    tokens = Lexer("(8 / 2) + 3 * 5;").tokens
    parser = Parser(tokens)
    tree = parser.parse(mode="repl")
    assert len(tree.body) == 1
    stmt = tree.body[0]
    assert isinstance(stmt, ExprStmt)
    tree_str = AstPrinter().visit(stmt.expression)
    print(tree_str)
