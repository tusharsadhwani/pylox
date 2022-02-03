from pylox.environment import Environment, EnvironmentLookupError
from pylox.errors import LoxError
from pylox.lox_types import LoxType, Number
from pylox.nodes import (
    Assignment,
    Binary,
    Block,
    ExprStmt,
    For,
    Grouping,
    If,
    Literal,
    Node,
    Print,
    Unary,
    VarDeclaration,
    Variable,
    While,
)
from pylox.tokens import TokenType
from pylox.utils import get_lox_type_name, is_truthy
from pylox.visitor import Visitor


class InterpreterError(LoxError):
    def __init__(self, message: str, node: Node) -> None:
        super().__init__(message, node.index)
        self.node = node


class Interpreter(Visitor[LoxType]):
    def __init__(self) -> None:
        self.environment = Environment()

    def visit_Literal(self, literal: Literal) -> LoxType:
        return literal.value

    def visit_Unary(self, unary: Unary) -> LoxType:
        if unary.operator.token_type == TokenType.MINUS:
            right_value = self.visit(unary.right)
            if not isinstance(right_value, Number):
                raise InterpreterError(
                    f"Expected number for unary '-', got {right_value}",
                    unary,
                )

            return -right_value

        elif unary.operator.token_type == TokenType.BANG:
            right_value = self.visit(unary.right)
            if is_truthy(right_value):
                return False

            return True

        raise NotImplementedError(
            f"Unary {unary.operator.token_type.value!r} not supported"
        )

    def visit_Binary(self, binary: Binary) -> LoxType:
        """Note that we evaluate both sides before type checking."""
        left_value = self.visit(binary.left)

        # Short circuited operators: `and` and `or`, can return early
        if binary.operator.token_type == TokenType.OR and is_truthy(left_value):
            return left_value
        if binary.operator.token_type == TokenType.AND and not is_truthy(left_value):
            return left_value

        right_value = self.visit(binary.right)

        # If short circuits didn't return early, they'll return the right value
        if binary.operator.token_type in (TokenType.AND, TokenType.OR):
            return right_value

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

        if isinstance(left_value, Number) and isinstance(right_value, Number):
            if binary.operator.token_type == TokenType.PLUS:
                return left_value + right_value
            if binary.operator.token_type == TokenType.MINUS:
                return left_value - right_value
            if binary.operator.token_type == TokenType.STAR:
                return left_value * right_value
            if binary.operator.token_type == TokenType.SLASH:
                # TODO: catch ZeroDivisionError
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
            f"{get_lox_type_name(left_value)!r} and {get_lox_type_name(right_value)!r}",
            binary,
        )

    def visit_Grouping(self, grouping: Grouping) -> LoxType:
        return self.visit(grouping.expression)

    def visit_Print(self, print_stmt: Print) -> None:
        value = self.visit(print_stmt.value)
        if value is None:
            print("nil")
        else:
            print(value)

    def visit_ExprStmt(self, expr_stmt: ExprStmt) -> None:
        self.visit(expr_stmt.expression)

    def visit_VarDeclaration(self, var_decl: VarDeclaration) -> None:
        if var_decl.initializer is None:
            value = None
        else:
            value = self.visit(var_decl.initializer)

        variable = var_decl.name.string
        self.environment.define(variable, value)

    def visit_Variable(self, variable: Variable) -> LoxType:
        try:
            return self.environment.get(variable.name.string)
        except EnvironmentLookupError as exc:
            raise InterpreterError(exc.message, variable)

    def visit_Assignment(self, assignment: Assignment) -> LoxType:
        value = self.visit(assignment.value)
        variable = assignment.name.string

        try:
            self.environment.assign(variable, value)
        except EnvironmentLookupError as exc:
            raise InterpreterError(exc.message, assignment)

        # Remember that assignment expressions return the assigned value
        return value

    def visit_Block(self, block: Block) -> None:
        own_environment = self.environment
        try:
            child_environment = Environment(self.environment)
            self.environment = child_environment
            self.visit(block)
        finally:
            self.environment = own_environment

    def visit_If(self, if_stmt: If) -> None:
        condition = self.visit(if_stmt.condition)
        if is_truthy(condition):
            self._evaluate(if_stmt.body)
        elif if_stmt.else_body is not None:
            self._evaluate(if_stmt.else_body)

    def visit_While(self, while_stmt: While) -> None:
        while is_truthy(self.visit(while_stmt.condition)):
            self._evaluate(while_stmt.body)

    def visit_For(self, for_stmt: For) -> None:
        if for_stmt.initializer is not None:
            self._evaluate(for_stmt.initializer)

        while for_stmt.condition is None or is_truthy(self.visit(for_stmt.condition)):
            self._evaluate(for_stmt.body)
            if for_stmt.increment is not None:
                self._evaluate(for_stmt.increment)
