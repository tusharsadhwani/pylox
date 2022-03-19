from __future__ import annotations

import sys
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Literal as LiteralType

from pylox.errors import LoxError
from pylox.lexer import Lexer
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
from pylox.tokens import EOF, Token, TokenType


class ParseError(LoxError):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(message, token.index)
        self.token = token


class ParseEOFError(ParseError):
    ...


class Parser:
    """
    Current grammar:
        program -> declaration* EOF
        declaration -> var_decl | function_decl | class_decl | statement
        var_decl -> "var" IDENTIFIER ("=" expression)? ";"
        function_decl -> "fun" function
        class_decl -> "class" IDENTIFIER ("<" IDENTIFIER)? "{" function* "}"
        function -> IDENTIFIER "(" parameters? ")" block
        parameters -> IDENTIFIER ("," IDENTIFIER)*
        statement -> block
                   | print_stmt
                   | if_stmt
                   | while_stmt
                   | for_stmt
                   | return_stmt
                   | expr_stmt
        block -> "{" declaration* "}"
        print_stmt -> "print" expression ";"
        if_stmt -> "if" "(" expression ")" statement ("else" statement)?
        while_stmt -> "while" "(" expression ")" statement
        for_stmt -> "for" "(" (var_decl | statement | ";")
                    expression? ";" expression? ")" statement
        return_stmt -> "return" expression? ";"
        expr_stmt -> expression ";"
        expression -> assignment
        assignment -> (call ".")? IDENTIFIER "=" assignment | logical_or
        logical_or -> logical_and ("or" logical_and)*
        logical_and -> equality ("and" equality)*
        equality -> comparison (("==" | "!=") comparison)*
        comparison -> term ((">" | ">=" | "<" | "<=") term)*
        term -> factor (("+" / "-") factor)*
        factor -> unary (("*" / "/") unary)*
        unary -> ("-" | "!") unary | call
        call -> primary ("(" arguments? ")")*
        arguments -> expression ("," expression)*
        primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")"
                | IDENTIFIER | "super" "." IDENTIFIER
    """

    def __init__(self, tokens: list[Token]) -> None:
        if len(tokens) == 0:
            raise ValueError("Cannot parse empty list of tokens")

        last_token = tokens[-1]
        if last_token != EOF:
            token_type = last_token.token_type.value
            raise ValueError(f"Expected EOF as the last token, found {token_type!r}")

        self.tokens = tokens
        self.index = 0

    @property
    def scanned(self) -> int:
        """Returns True if tokens has been fully scanned."""
        if self.index >= len(self.tokens) - 1:
            return True

        return False

    def advance(self) -> None:
        self.index += 1

    def get_token(self) -> Token:
        if self.scanned:
            return EOF

        return self.tokens[self.index]

    def get_index(self) -> int:
        if self.index == 0:
            return self.get_token().index

        return self.previous().index

    def peek_next(self, token_type: TokenType) -> bool:
        token = self.get_token()

        if token is EOF:
            return False

        return token.token_type == token_type

    def match_next(self, *token_types: TokenType) -> bool:
        token = self.get_token()

        if token is EOF:
            return False

        if token.token_type in token_types:
            self.advance()
            return True

        return False

    def previous(self) -> Token:
        return self.tokens[self.index - 1]

    def synchronize(self) -> None:
        """
        Current synchronization process: keep scanning till next statement
        (a.k.a. find a semicolon).
        """
        while not self.scanned and not self.match_next(
            TokenType.SEMICOLON, TokenType.RIGHT_BRACE
        ):
            self.advance()

    @overload
    def parse(
        self, mode: LiteralType["file"] = "file"
    ) -> tuple[Program, list[ParseError]]:
        ...

    @overload
    def parse(self, mode: LiteralType["repl"]) -> Program:
        ...

    def parse(
        self, mode: LiteralType["file", "repl"] = "file"
    ) -> Program | tuple[Program, list[ParseError]]:
        body: list[Stmt] = []
        # Errors are only stored in mode == "file"
        errors: list[ParseError] = []

        index = self.get_index()
        while not self.scanned:
            try:
                body.append(self.parse_declaration())
            except ParseError as exc:
                if mode == "repl":
                    raise

                errors.append(exc)
                self.synchronize()

        program = Program(body, index=index)
        return (program, errors) if mode == "file" else program

    def parse_declaration(self) -> Stmt:
        if self.match_next(TokenType.VAR):
            return self.parse_var_declaration()

        if self.match_next(TokenType.FUN):
            return self.parse_function_declaration()

        if self.match_next(TokenType.CLASS):
            return self.parse_class_declaration()

        return self.parse_statement()

    def parse_var_declaration(self) -> VarDeclaration:
        index = self.get_index()
        name = self.consume(TokenType.IDENTIFIER)

        if not self.match_next(TokenType.EQUAL):
            self.consume(TokenType.SEMICOLON)
            return VarDeclaration(name, index=index)

        initializer = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return VarDeclaration(name, initializer, index=index)

    def parse_function_declaration(
        self,
        kind: LiteralType["function", "method"] = "function",
    ) -> FunctionDef:
        index = self.get_index()

        function_name = self.consume(TokenType.IDENTIFIER, name=f"{kind} name")
        bracket = self.consume(TokenType.LEFT_PAREN)

        parameters: list[Token] = []
        # Case 1: No parameters
        if self.match_next(TokenType.RIGHT_PAREN):
            self.consume(TokenType.LEFT_BRACE)
            block = self.parse_block()
            return FunctionDef(function_name, parameters, block.body, index=index)

        # Case 2: One parameter
        parameter = self.consume(TokenType.IDENTIFIER, name="parameter name")
        parameters.append(parameter)
        if self.match_next(TokenType.RIGHT_PAREN):
            self.consume(TokenType.LEFT_BRACE)
            block = self.parse_block()
            return FunctionDef(function_name, parameters, block.body, index=index)

        # Case 3: upto 255 arguments, preceded by a comma
        while self.match_next(TokenType.COMMA):
            # Only upto 255 arguments allowed
            if len(parameters) >= 255:
                raise ParseError(
                    "More than 255 parameters not allowed in a function definition",
                    bracket,
                )

            parameter = self.consume(TokenType.IDENTIFIER, name="parameter name")
            parameters.append(parameter)

        self.consume(TokenType.RIGHT_PAREN)
        self.consume(TokenType.LEFT_BRACE)
        block = self.parse_block()
        return FunctionDef(function_name, parameters, block.body, index=index)

    def parse_class_declaration(self) -> Stmt:
        index = self.get_index()

        name = self.consume(TokenType.IDENTIFIER, name="class name")

        superclass = None
        if self.match_next(TokenType.LESS):
            superclass_name = self.consume(TokenType.IDENTIFIER, name="superclass name")
            superclass = Variable(superclass_name)

        self.consume(TokenType.LEFT_BRACE)

        methods: list[FunctionDef] = []
        while not self.scanned and not self.peek_next(TokenType.RIGHT_BRACE):
            methods.append(self.parse_function_declaration(kind="method"))

        self.consume(TokenType.RIGHT_BRACE)
        return ClassDef(name, superclass, methods, index=index)

    def parse_statement(self) -> Stmt:
        if self.match_next(TokenType.LEFT_BRACE):
            return self.parse_block()

        if self.match_next(TokenType.PRINT):
            return self.parse_print_stmt()

        if self.match_next(TokenType.IF):
            return self.parse_if_stmt()

        if self.match_next(TokenType.WHILE):
            return self.parse_while_stmt()

        if self.match_next(TokenType.FOR):
            return self.parse_for_stmt()

        if self.match_next(TokenType.RETURN):
            return self.parse_return_stmt()

        return self.parse_expr_stmt()

    def parse_block(self) -> Block:
        index = self.get_index()
        statements = self.parse_block_statements()
        self.consume(TokenType.RIGHT_BRACE)
        return Block(body=statements, index=index)

    def parse_block_statements(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.scanned and not self.peek_next(TokenType.RIGHT_BRACE):
            statements.append(self.parse_declaration())

        return statements

    def parse_print_stmt(self) -> Print:
        index = self.get_index()
        expression = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return Print(expression, index=index)

    def parse_if_stmt(self) -> If:
        index = self.get_index()
        self.consume(TokenType.LEFT_PAREN)
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN)
        body = self.parse_declaration()

        if self.match_next(TokenType.ELSE):
            else_body = self.parse_declaration()
            return If(condition, body, else_body, index=index)

        return If(condition, body, index=index)

    def parse_while_stmt(self) -> While:
        index = self.get_index()
        self.consume(TokenType.LEFT_PAREN)
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN)
        body = self.parse_declaration()
        return While(condition, body, index=index)

    def parse_for_stmt(self) -> For:
        index = self.get_index()
        self.consume(TokenType.LEFT_PAREN)

        # Step 1: Initializer (optional)
        initializer: VarDeclaration | Stmt | None
        if self.match_next(TokenType.SEMICOLON):
            initializer = None
        elif self.match_next(TokenType.VAR):
            initializer = self.parse_var_declaration()
        else:
            initializer = self.parse_statement()

        # Step 2: Condition (optional)
        if self.match_next(TokenType.SEMICOLON):
            condition = None
        else:
            condition = self.parse_expression()
            self.consume(TokenType.SEMICOLON)

        # Step 3: Increment (optional)
        if self.match_next(TokenType.RIGHT_PAREN):
            increment = None
        else:
            increment = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN)

        body = self.parse_declaration()
        return For(initializer, condition, increment, body, index=index)

    def parse_return_stmt(self) -> ReturnStmt:
        keyword = self.previous()

        if self.match_next(TokenType.SEMICOLON):
            return ReturnStmt(keyword)

        expression = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return ReturnStmt(keyword, expression, index=keyword.index)

    def parse_expr_stmt(self) -> ExprStmt:
        expression = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return ExprStmt(expression, index=expression.index)

    def parse_expression(self) -> Expr:
        return self.parse_assignment()

    def parse_assignment(self) -> Expr:
        expr = self.parse_logical_or()
        if self.match_next(TokenType.EQUAL):
            equals_token = self.previous()

            value = self.parse_assignment()
            if isinstance(expr, Variable):
                return Assignment(expr.name, value, index=expr.index)

            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value, index=expr.index)

            else:
                type_name = expr.__class__.__name__
                raise ParseError(
                    f"Invalid assign target: {type_name!r}",
                    equals_token,
                )

        # If it's not assignment, it's equality (or anything below)
        return expr

    def parse_logical_or(self) -> Expr:
        left = self.parse_logical_and()
        while self.match_next(TokenType.OR):
            or_token = self.previous()
            right = self.parse_logical_and()

            left = Binary(left, or_token, right, index=left.index)

        return left

    def parse_logical_and(self) -> Expr:
        left = self.parse_equality()
        while self.match_next(TokenType.AND):
            or_token = self.previous()
            right = self.parse_equality()

            left = Binary(left, or_token, right, index=left.index)

        return left

    def parse_equality(self) -> Expr:
        left = self.parse_comparison()

        while self.match_next(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.parse_comparison()

            left = Binary(left, operator, right, index=left.index)

        return left

    def parse_comparison(self) -> Expr:
        left = self.parse_term()

        while self.match_next(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.parse_term()

            left = Binary(left, operator, right, index=left.index)

        return left

    def parse_term(self) -> Expr:
        left = self.parse_factor()

        while self.match_next(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.parse_factor()

            left = Binary(left, operator, right, index=left.index)

        return left

    def parse_factor(self) -> Expr:
        left = self.parse_unary()

        while self.match_next(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self.previous()
            right = self.parse_unary()

            left = Binary(left, operator, right, index=left.index)

        return left

    def parse_unary(self) -> Expr:
        if self.match_next(TokenType.MINUS, TokenType.BANG):
            operator = self.previous()
            right = self.parse_unary()
            return Unary(operator, right, index=operator.index)

        return self.parse_call_or_get()

    def parse_call_or_get(self) -> Expr:
        expr = self.parse_primary()

        while True:
            if self.peek_next(TokenType.LEFT_PAREN):
                expr = self.parse_call(expr)

            elif self.match_next(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, name="property name")
                expr = Get(expr, name, index=expr.index)

            else:
                break  # pragma: no cover -- bug with Python parser upto 3.9

        return expr

    def parse_call(self, callee: Expr) -> Expr:
        while self.match_next(TokenType.LEFT_PAREN):
            bracket = self.previous()

            # Case 1: No arguments
            if self.match_next(TokenType.RIGHT_PAREN):
                # TODO: maybe we should be using bracket.index here?
                # the whole call expression does span from callee to
                # RIGHT_PAREN, but in an error message, pointing at the
                # right LEFT_PAREN might be more helpful.
                # Figure out a consistent answer.
                callee = Call(callee, bracket, index=callee.index)
                continue

            arguments: list[Expr] = []

            # Case 2: One argument
            arguments.append(self.parse_expression())
            if self.match_next(TokenType.RIGHT_PAREN):
                callee = Call(callee, bracket, arguments, index=callee.index)
                continue

            # Case 3: upto 255 arguments, preceded by a comma
            while self.match_next(TokenType.COMMA):
                # Only upto 255 arguments allowed
                if len(arguments) >= 255:
                    raise ParseError(
                        "More than 255 arguments not allowed in a function call",
                        bracket,
                    )

                arguments.append(self.parse_expression())

            self.consume(TokenType.RIGHT_PAREN)
            callee = Call(callee, bracket, arguments, index=callee.index)

        return callee

    def parse_primary(self) -> Expr:
        if self.scanned:
            eof_token = self.get_token()
            raise ParseEOFError("Unexpected end of file while parsing", eof_token)

        if self.match_next(TokenType.STRING, TokenType.NUMBER):
            token = self.previous()
            return Literal(token.value, index=token.index)

        if self.match_next(TokenType.TRUE):
            return Literal(True, index=self.get_index())
        if self.match_next(TokenType.FALSE):
            return Literal(False, index=self.get_index())
        if self.match_next(TokenType.NIL):
            return Literal(None, index=self.get_index())

        if self.match_next(TokenType.THIS):
            return This(self.previous(), index=self.get_index())

        if self.match_next(TokenType.SUPER):
            token = self.previous()
            self.consume(TokenType.DOT)
            method_token = self.consume(TokenType.IDENTIFIER, name="method name")
            method = Variable(method_token)
            return Super(token, method, index=self.get_index())

        if self.match_next(TokenType.IDENTIFIER):
            token = self.previous()
            return Variable(token, index=token.index)

        if self.match_next(TokenType.LEFT_PAREN):
            index = self.get_index()
            expression = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN)
            return Grouping(expression, index=index)

        token = self.get_token()
        raise ParseError(f"Unexpected token: {token.string!r}", token)

    def consume(self, expected_type: TokenType, name: str = "") -> Token:
        """Consumes one token. If it's not of the expected type, throws."""
        if name:
            expected = name
        else:
            expected = repr(expected_type.value)

        token = self.get_token()

        if token == EOF:
            raise ParseEOFError(
                f"Expected to find {expected}, found EOF",
                token,
            )

        if token.token_type != expected_type:
            raise ParseError(
                f"Expected to find {expected}, found {token.string!r}",
                token,
            )

        self.advance()
        return token


if __name__ == "__main__":
    _source = " ".join(sys.argv[1:])
    _tokens = Lexer(_source).tokens

    _parser = Parser(_tokens)
    _program, _ = _parser.parse()
    print(_program)
