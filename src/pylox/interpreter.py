from __future__ import annotations

import time

from pylox.environment import Environment, EnvironmentLookupError
from pylox.errors import LoxError
from pylox.lox_types import LoxType, Number
from pylox.nodes import (
    Assignment,
    Binary,
    Block,
    Call,
    ClassDef,
    Expr,
    ExprStmt,
    For,
    FunctionDef,
    Get,
    Grouping,
    If,
    Literal,
    Node,
    Print,
    Program,
    ReturnStmt,
    Set,
    Stmt,
    Super,
    This,
    Unary,
    VarDeclaration,
    Variable,
    While,
)
from pylox.tokens import TokenType
from pylox.utils import get_lox_type_name, is_lox_callable, is_truthy
from pylox.visitor import Visitor


class NativeClock:
    def __repr__(self) -> str:
        return "<native function 'clock'>"

    @staticmethod
    def call(_: Interpreter, __: list[LoxType]) -> Number:
        return time.time()

    @staticmethod
    def arity() -> int:
        return 0


def create_globals() -> Environment:
    globals = Environment()
    globals.define("clock", NativeClock())
    return globals


class Return(Exception):
    """Used to return a value from inside an executing function"""

    def __init__(self, value: LoxType) -> None:
        self.value = value


class LoxFunction:
    def __init__(self, declaration: FunctionDef, closure: Environment) -> None:
        self.declaration = declaration
        self.closure = closure

    def __repr__(self) -> str:
        function_name = self.declaration.name.string
        return f"<function {function_name!r}>"

    def arity(self) -> int:
        return len(self.declaration.parameters)

    def call(self, interpreter: Interpreter, arguments: list[LoxType]) -> LoxType:
        # Each function call creates a new local environment
        environment = Environment(self.closure)
        for parameter, argument in zip(self.declaration.parameters, arguments):
            # First, define the arguments
            environment.define(parameter.string, argument)

        # Then, run the code in the new context
        # TODO: there's similar code in visit_Block. Refactor?
        parent_enviroment = interpreter.environment
        interpreter.environment = environment

        try:
            for statement in self.declaration.body:
                interpreter.execute(statement)
        except Return as ret:
            return ret.value
        finally:
            interpreter.environment = parent_enviroment

        return None

    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment)


class LoxClass:
    def __init__(
        self,
        name: str,
        superclass: LoxClass | None,
        methods: dict[str, LoxFunction],
    ) -> None:
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __repr__(self) -> str:
        return f"<class {self.name!r}>"

    def find_method(self, name: str) -> LoxFunction | None:
        if name in self.methods:
            method = self.methods[name]
            return method

        if self.superclass is not None:
            return self.superclass.find_method(name)

        return None

    def call(self, interpreter: Interpreter, arguments: list[LoxType]) -> LoxType:
        instance = LoxInstance(self)

        initializer = self.methods.get("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def arity(self) -> int:
        initializer = self.methods.get("init")
        if initializer is None:
            return 0

        return initializer.arity()


class LoxInstance:
    def __init__(self, class_object: LoxClass) -> None:
        self.class_object = class_object
        self.fields: dict[str, LoxType] = {}

    def __repr__(self) -> str:
        return f"<object of {self.class_object.name!r}>"

    def get(self, name: str) -> LoxType:
        if name in self.fields:
            return self.fields[name]

        method = self.class_object.find_method(name)
        if method is not None:
            return method.bind(self)

        raise LookupError(f"No attribute {name!r} found on {self!r}")

    def set(self, name: str, value: LoxType) -> None:
        self.fields[name] = value


class InterpreterError(LoxError):
    def __init__(self, message: str, node: Node) -> None:
        super().__init__(message, node.index)
        self.node = node


class Interpreter(Visitor[LoxType]):
    def __init__(self) -> None:
        self.globals = create_globals()
        self.environment = self.globals
        self.locals: dict[Expr, int] = {}

    def visit(self, node: Program | Block) -> None:
        for stmt in node.body:
            self.generic_visit(stmt)

    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

    def execute(self, stmt: Stmt) -> None:
        self.generic_visit(stmt)

    def evaluate(self, expr: Expr) -> LoxType:
        return self.generic_visit(expr)

    def lookup(self, name: str, expr: Expr) -> LoxType:
        depth = self.locals.get(expr)
        if depth is not None:
            return self.environment.get_at(depth, name)

        try:
            return self.globals.get(name)
        except EnvironmentLookupError as exc:
            raise InterpreterError(exc.message, expr)

    @staticmethod
    def visit_Literal(literal: Literal) -> LoxType:
        return literal.value

    def visit_Unary(self, unary: Unary) -> LoxType:
        if unary.operator.token_type == TokenType.MINUS:
            right_value = self.evaluate(unary.right)
            if not isinstance(right_value, Number):
                value_type = get_lox_type_name(right_value)
                raise InterpreterError(
                    f"Expected 'Number' for unary '-', got {value_type!r}",
                    unary,
                )

            return -right_value

        elif unary.operator.token_type == TokenType.BANG:
            right_value = self.evaluate(unary.right)
            if is_truthy(right_value):
                return False

            return True

        raise NotImplementedError(
            f"Unary {unary.operator.token_type.value!r} not supported"
        )

    def visit_Binary(self, binary: Binary) -> LoxType:
        """Note that we evaluate both sides before type checking."""
        left_value = self.evaluate(binary.left)

        # Short circuited operators: `and` and `or`, can return early
        if binary.operator.token_type == TokenType.OR and is_truthy(left_value):
            return left_value
        if binary.operator.token_type == TokenType.AND and not is_truthy(left_value):
            return left_value

        right_value = self.evaluate(binary.right)

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
                if right_value == 0:
                    raise InterpreterError("Division by zero", binary.right)
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
        return self.evaluate(grouping.expression)

    def visit_Print(self, print_stmt: Print) -> None:
        value = self.evaluate(print_stmt.value)
        if value is None:
            print("nil")
        elif value is True:
            print("true")
        elif value is False:
            print("false")
        else:
            print(value)

    def visit_ExprStmt(self, expr_stmt: ExprStmt) -> None:
        self.evaluate(expr_stmt.expression)

    def visit_VarDeclaration(self, var_decl: VarDeclaration) -> None:
        if var_decl.initializer is None:
            value = None
        else:
            value = self.evaluate(var_decl.initializer)

        variable = var_decl.name.string
        self.environment.define(variable, value)

    def visit_Variable(self, variable: Variable) -> LoxType:
        return self.lookup(variable.name.string, variable)

    def visit_Assignment(self, assignment: Assignment) -> LoxType:
        value = self.evaluate(assignment.value)
        variable = assignment.name.string

        depth = self.locals.get(assignment)
        if depth is not None:
            self.environment.assign_at(depth, variable, value)
            return value

        try:
            self.globals.assign(variable, value)
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
        condition = self.evaluate(if_stmt.condition)
        if is_truthy(condition):
            self.execute(if_stmt.body)
        elif if_stmt.else_body is not None:
            self.execute(if_stmt.else_body)

    def visit_While(self, while_stmt: While) -> None:
        while is_truthy(self.evaluate(while_stmt.condition)):
            self.execute(while_stmt.body)

    def visit_For(self, for_stmt: For) -> None:
        if for_stmt.initializer is not None:
            self.execute(for_stmt.initializer)

        while for_stmt.condition is None or is_truthy(
            self.evaluate(for_stmt.condition)
        ):
            self.execute(for_stmt.body)
            if for_stmt.increment is not None:
                self.evaluate(for_stmt.increment)

    def visit_Call(self, call: Call) -> LoxType:
        function = self.evaluate(call.callee)

        # We will evaluate all arguments before checking if the function
        # is callable. This is done because that's what a programmer
        # would expect to happen. Seeing abc(xyz()), you'd expect xyz()
        # to finish before abc(...) is attempted.
        arguments: list[LoxType] = []
        for argument in call.arguments:
            arguments.append(self.evaluate(argument))

        if not is_lox_callable(function):
            object_type = get_lox_type_name(function)
            raise InterpreterError(f"{object_type!r} object is not callable", call)

        if function.arity() != len(arguments):
            expected = function.arity()
            got = len(arguments)
            raise InterpreterError(
                f"{function!r} expected {expected} arguments, got {got}", call
            )

        return function.call(self, arguments)

    def visit_FunctionDef(self, function_def: FunctionDef) -> None:
        function_object = LoxFunction(function_def, self.environment)
        self.environment.define(function_def.name.string, function_object)

    def visit_ReturnStmt(self, return_stmt: ReturnStmt) -> None:
        if return_stmt.value:
            return_value = self.evaluate(return_stmt.value)
        else:
            return_value = None

        raise Return(return_value)

    def visit_ClassDef(self, class_def: ClassDef) -> None:

        # We want `super` to be defined in a new environment
        class_environment = self.environment
        super_environment = Environment(class_environment)
        self.environment = super_environment

        superclass = None
        if class_def.superclass is not None:
            superclass_value = self.evaluate(class_def.superclass)
            if not isinstance(superclass_value, LoxClass):
                superclass_type = get_lox_type_name(superclass_value)
                raise InterpreterError(
                    f"Can only inherit from classes, found {superclass_type!r}",
                    class_def.superclass,
                )
            superclass = superclass_value
            self.environment.define("super", superclass_value)

        # We also want the methods to be able to access `super`
        methods: dict[str, LoxFunction] = {}
        for method in class_def.methods:
            method_object = LoxFunction(method, self.environment)
            methods[method.name.string] = method_object

        # Reset it back once all methods use the super environment
        self.environment = class_environment
        class_object = LoxClass(class_def.name.string, superclass, methods)
        self.environment.define(class_def.name.string, class_object)

    def visit_Get(self, get: Get) -> LoxType:
        obj = self.evaluate(get.object)
        if not isinstance(obj, LoxInstance):
            raise InterpreterError(
                f"Cannot access properties inside {get_lox_type_name(obj)!r}",
                get.object,
            )

        attribute = get.name.string
        try:
            return obj.get(attribute)
        except LookupError:
            raise InterpreterError(
                f"{obj.class_object.name!r} object has no attribute {attribute!r}", get
            )

    def visit_Set(self, set: Set) -> LoxType:
        obj = self.evaluate(set.object)
        if not isinstance(obj, LoxInstance):
            raise InterpreterError(
                f"Cannot set properties on {get_lox_type_name(obj)!r}",
                set.object,
            )

        value = self.evaluate(set.value)
        obj.set(set.name.string, value)

        # Similar to visit_Assign, we return the set value
        return value

    def visit_This(self, this: This) -> LoxType:
        return self.lookup("this", this)

    def visit_Super(self, super: Super) -> LoxType:
        depth = self.locals[super]
        superclass = self.environment.get_at(depth, "super")
        instance = self.environment.get_at(depth - 1, "this")

        assert isinstance(superclass, LoxClass)
        assert isinstance(instance, LoxInstance)

        super_method = superclass.find_method(super.method.name.string)
        assert super_method is not None
        return super_method.bind(instance)
