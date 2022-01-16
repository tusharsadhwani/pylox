from pylox.expr import Binary, Grouping, Literal, Unary
from pylox.tokens import TokenType
from pylox.utils import get_lox_type_name
from pylox.visitor import Visitor


class InterpreterError(Exception):
    ...


class Interpreter(Visitor[object]):
    def visit_Literal(self, literal: Literal) -> object:
        return literal.value

    def visit_Unary(self, unary: Unary) -> object:
        if unary.operator.token_type == TokenType.MINUS:
            right_value = self.visit(unary.right)
            if not isinstance(right_value, float):
                raise InterpreterError(
                    f"Expected number for unary '-', got {right_value}"
                )

            return -right_value

        # TODO: unary `!`
        raise NotImplementedError(
            f"Unary {unary.operator.token_type.value!r} not supported"
        )

    def visit_Binary(self, binary: Binary) -> object:
        """Note that we evaluate both sides before type checking."""
        left_value = self.visit(binary.left)
        right_value = self.visit(binary.right)

        if binary.operator.token_type == TokenType.EQUAL_EQUAL:
            return left_value == right_value
        if binary.operator.token_type == TokenType.BANG_EQUAL:
            return left_value != right_value

        if (
            isinstance(left_value, str)
            and isinstance(right_value, str)
            and binary.operator.token_type == TokenType.PLUS
        ):
            return left_value + right_value

        if isinstance(left_value, float) and isinstance(right_value, float):
            if binary.operator.token_type == TokenType.PLUS:
                return left_value + right_value
            if binary.operator.token_type == TokenType.MINUS:
                return left_value - right_value
            if binary.operator.token_type == TokenType.STAR:
                return left_value * right_value
            if binary.operator.token_type == TokenType.SLASH:
                return left_value / right_value
            if binary.operator.token_type == TokenType.PERCENT:
                return left_value % right_value

            if binary.operator.token_type == TokenType.GREATER:
                return left_value > right_value
            if binary.operator.token_type == TokenType.GREATER_EQUAL:
                return left_value >= right_value
            if binary.operator.token_type == TokenType.LESS:
                return left_value < right_value
            if binary.operator.token_type == TokenType.LESS_EQUAL:
                return left_value <= right_value

        raise InterpreterError(
            f"Unsupported types for {binary.operator.token_type.value!r}: "
            f"{get_lox_type_name(left_value)!r} and {get_lox_type_name(right_value)!r}"
        )

    def visit_Grouping(self, grouping: Grouping) -> object:
        return self.visit(grouping.expression)
