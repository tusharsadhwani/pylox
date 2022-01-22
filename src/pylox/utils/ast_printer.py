from pylox.lexer import Lexer
from pylox.nodes import Binary, Expr, Grouping, Literal, Unary, Variable
from pylox.parser import Parser
from pylox.visitor import Visitor


class AstPrinter(Visitor[str]):
    # TODO: Find a way for mypy to enforce every visit function's
    # return value to be str.
    def visit_Expr(self, expr: Expr) -> str:
        return ""  # TODO: remove this visitor, as empty file shouldn't return Expr()

    def visit_Literal(self, literal: Literal) -> str:
        if literal.value is None:
            return "nil"

        if isinstance(literal.value, bool):
            return f"{literal.value}".lower()

        # TODO: replace these two with "literal.value!r" once single quotes are added
        if isinstance(literal.value, str):
            return f'"{literal.value}"'

        return f"{literal.value}"

    def visit_Variable(self, variable: Variable) -> str:
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


def main() -> None:
    tokens = Lexer("(8 / 2) + 3 * 5").tokens
    parser = Parser(tokens)
    tree = parser.parse()
    tree_str = AstPrinter().visit(tree)
    print(tree_str)


if __name__ == "__main__":
    main()
