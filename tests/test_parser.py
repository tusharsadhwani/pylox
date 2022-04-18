from __future__ import annotations

import os

import pytest

from pylox.lexer import Lexer
from pylox.nodes import (
    Assignment,
    Binary,
    Block,
    Call,
    ExprStmt,
    Get,
    Grouping,
    Literal,
    Print,
    Program,
    Set,
    VarDeclaration,
    Variable,
)
from pylox.parser import Parser
from pylox.tokens import EOF, Token, TokenType
from pylox.utils.ast_printer import AstPrinter


def read_file(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


def test_parser_no_eof() -> None:
    with pytest.raises(ValueError) as exc:
        Parser([])

    assert exc.value.args[0] == "Cannot parse empty list of tokens"

    tokens = [Token(TokenType.VAR, "var"), Token(TokenType.IDENTIFIER, "x")]
    with pytest.raises(ValueError) as exc:
        Parser(tokens)

    assert exc.value.args[0] == "Expected EOF as the last token, found 'Identifier'"


@pytest.mark.parametrize(
    ("tokens", "expected_tree"),
    (
        ([Token(TokenType.IDENTIFIER, "abc"), EOF], "abc"),
        ([Token(TokenType.NIL, "nil"), EOF], "nil"),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.INTEGER, "1", 1),
                EOF,
            ],
            "(a + 1)",
        ),
        (
            [
                Token(TokenType.STRING, '"abc"', "abc"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.STRING, '"xyz"', "xyz"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.IDENTIFIER, "rest"),
                EOF,
            ],
            "(('abc' + 'xyz') + rest)",
        ),
        (
            [
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.SLASH, "/"),
                Token(TokenType.IDENTIFIER, "y"),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.INTEGER, "2", 2),
                Token(TokenType.STAR, "*"),
                Token(TokenType.IDENTIFIER, "z"),
                EOF,
            ],
            "((group (x / y)) + (2 * z))",
        ),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "c"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "5"),
                EOF,
            ],
            "(((a == b) == c) == 5)",
        ),
        (
            [
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "y"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.TRUE, "true"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.INTEGER, "2", 2),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.INTEGER, "3", 3),
                Token(TokenType.BANG_EQUAL, "!="),
                Token(TokenType.INTEGER, "10", 10),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.BANG_EQUAL, "!="),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.INTEGER, "1", 1),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.INTEGER, "3", 3),
                Token(TokenType.GREATER, ">"),
                Token(TokenType.INTEGER, "5", 5),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.RIGHT_PAREN, ")"),
                EOF,
            ],
            """
            (((x == y) == true) == 
                (group
                    ((group ((2 + 3) != 10))
                    !=
                    (group ((1 + 3) > 5)))))
            """,
        ),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.AND, "and"),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.OR, "or"),
                Token(TokenType.TRUE, "true"),
                Token(TokenType.AND, "and"),
                Token(TokenType.FALSE, "false"),
                Token(TokenType.AND, "and"),
                Token(TokenType.BANG, "!"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.OR, "or"),
                Token(TokenType.IDENTIFIER, "y"),
                Token(TokenType.AND, "and"),
                Token(TokenType.IDENTIFIER, "z"),
                EOF,
            ],
            "(((a and b) or ((true and false) and (! x))) or (y and z))",
        ),
        (
            [
                Token(TokenType.IDENTIFIER, "fibonacci"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.INTEGER, "5", 5),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "fibonacci"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.INTEGER, "4", 4),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.IDENTIFIER, "fibonacci"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.INTEGER, "3", 3),
                Token(TokenType.RIGHT_PAREN, ")"),
                EOF,
            ],
            "((fibonacci 5) == ((fibonacci 4) + (fibonacci 3)))",
        ),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.INTEGER, "10", 10),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.INTEGER, "20", 20),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.INTEGER, "30", 30),
                Token(TokenType.RIGHT_PAREN, ")"),
                EOF,
            ],
            "(((a 10) 20) 30)",
        ),
    ),
)
def test_parser_exprs(tokens: list[Token], expected_tree: str) -> None:
    parser = Parser(tokens)
    expression = parser.parse_expression()
    tree_str = AstPrinter().visit(expression)
    assert " ".join(tree_str.split()) == " ".join(expected_tree.split())


@pytest.mark.parametrize(
    ("filename", "expected_tree"),
    (
        (
            "expression.lox",
            "(2 + (3 * 5))",
        ),
        (
            "expression_long.lox",
            """
            ((group
                ((((2 > 3) > (4 + 5)) != x) == ((y * z) / w)))
                == (false + true))
            """,
        ),
    ),
)
def test_parser_expr_files(filename: str, expected_tree: str) -> None:
    test_dir = os.path.join(os.path.dirname(__file__), "testdata")
    filepath = os.path.join(test_dir, filename)
    source = read_file(filepath)

    tokens = Lexer(source).tokens
    parser = Parser(tokens)
    expression = parser.parse_expression()
    tree_str = AstPrinter().visit(expression)
    assert " ".join(tree_str.split()) == " ".join(expected_tree.split())


@pytest.mark.parametrize(
    ("tokens", "expected_tree"),
    (
        (
            [
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.SEMICOLON, ";"),
                EOF,
            ],
            Program(
                body=[
                    VarDeclaration(
                        name=Token(TokenType.IDENTIFIER, "x"),
                    ),
                ]
            ),
        ),
        (
            [
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.INTEGER, "5", 5),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.PRINT, "print"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.SEMICOLON, ";"),
                EOF,
            ],
            Program(
                body=[
                    VarDeclaration(
                        name=Token(TokenType.IDENTIFIER, "x"),
                        initializer=Literal(5),
                    ),
                    Print(Variable(Token(TokenType.IDENTIFIER, "x"))),
                ]
            ),
        ),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.INTEGER, "2", 2),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.INTEGER, "3", 3),
                Token(TokenType.SEMICOLON, ";"),
                EOF,
            ],
            Program(
                body=[
                    ExprStmt(
                        Assignment(
                            name=Token(TokenType.IDENTIFIER, "a"),
                            value=Assignment(
                                name=Token(TokenType.IDENTIFIER, "b"),
                                value=Binary(
                                    left=Literal(2),
                                    operator=Token(TokenType.PLUS, "+"),
                                    right=Literal(3),
                                ),
                            ),
                        ),
                    ),
                ],
            ),
        ),
        (
            [
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.INTEGER, "5", 5),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.LEFT_BRACE, "{"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.INTEGER, "10", 10),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.LEFT_BRACE, "{"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.INTEGER, "20", 20),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.RIGHT_BRACE, "}"),
                Token(TokenType.RIGHT_BRACE, "}"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.INTEGER, "40", 40),
                Token(TokenType.SEMICOLON, ";"),
                EOF,
            ],
            Program(
                body=[
                    VarDeclaration(
                        name=Token(TokenType.IDENTIFIER, "x"),
                        initializer=Literal(5),
                    ),
                    Block(
                        body=[
                            VarDeclaration(
                                name=Token(TokenType.IDENTIFIER, "x"),
                                initializer=Literal(10),
                            ),
                            Block(
                                body=[
                                    VarDeclaration(
                                        name=Token(TokenType.IDENTIFIER, "x"),
                                        initializer=Literal(20),
                                    ),
                                ]
                            ),
                        ]
                    ),
                    VarDeclaration(
                        name=Token(TokenType.IDENTIFIER, "x"),
                        initializer=Literal(40),
                    ),
                ]
            ),
        ),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.DOT, "."),
                Token(TokenType.IDENTIFIER, "b"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.DOT, "."),
                Token(TokenType.IDENTIFIER, "c"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.IDENTIFIER, "y"),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.DOT, "."),
                Token(TokenType.IDENTIFIER, "d"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.IDENTIFIER, "z"),
                Token(TokenType.SEMICOLON, ";"),
                EOF,
            ],
            Program(
                body=[
                    ExprStmt(
                        expression=Set(
                            object=Call(
                                callee=Get(
                                    object=Call(
                                        callee=Get(
                                            object=Variable(
                                                name=Token(TokenType.IDENTIFIER, "a")
                                            ),
                                            name=Token(TokenType.IDENTIFIER, "b"),
                                        ),
                                        paren=Token(TokenType.LEFT_PAREN, "("),
                                        arguments=[
                                            Variable(
                                                name=Token(TokenType.IDENTIFIER, "x")
                                            )
                                        ],
                                    ),
                                    name=Token(TokenType.IDENTIFIER, "c"),
                                ),
                                paren=Token(TokenType.LEFT_PAREN, "("),
                                arguments=[
                                    Variable(name=Token(TokenType.IDENTIFIER, "y"))
                                ],
                            ),
                            name=Token(TokenType.IDENTIFIER, "d"),
                            value=Variable(name=Token(TokenType.IDENTIFIER, "z")),
                        )
                    )
                ]
            ),
        ),
    ),
)
def test_parser(tokens: list[Token], expected_tree: Program) -> None:
    parser = Parser(tokens)
    program, errors = parser.parse()
    assert not errors
    assert program == expected_tree


@pytest.mark.parametrize(
    ("filename", "expected_tree"),
    (
        (
            "simple.lox",
            Program(
                body=[
                    Print(Literal("Hello", index=6), index=0),
                    VarDeclaration(
                        name=Token(TokenType.IDENTIFIER, "a", index=19),
                        initializer=Literal(5, index=23),
                        index=15,
                    ),
                    Print(
                        Variable(Token(TokenType.IDENTIFIER, "a", index=32), index=32),
                        index=26,
                    ),
                    VarDeclaration(
                        name=Token(TokenType.IDENTIFIER, "a", index=39),
                        initializer=Literal(False, index=43),
                        index=35,
                    ),
                    Print(
                        Variable(Token(TokenType.IDENTIFIER, "a", index=56), index=56),
                        index=50,
                    ),
                    Print(
                        Grouping(
                            expression=Binary(
                                left=Binary(
                                    left=Literal(6.75, index=66),
                                    operator=Token(TokenType.STAR, "*", index=71),
                                    right=Grouping(
                                        expression=Binary(
                                            left=Literal(3, index=74),
                                            operator=Token(
                                                TokenType.PLUS, "+", index=76
                                            ),
                                            right=Literal(5, index=78),
                                            index=74,
                                        ),
                                        index=73,
                                    ),
                                    index=66,
                                ),
                                operator=Token(TokenType.SLASH, "/", index=81),
                                right=Literal(2, index=83),
                                index=66,
                            ),
                            index=65,
                        ),
                        index=59,
                    ),
                ],
                index=0,
            ),
        ),
    ),
)
def test_parser_files(filename: str, expected_tree: Program) -> None:
    test_dir = os.path.join(os.path.dirname(__file__), "testdata")
    filepath = os.path.join(test_dir, filename)
    source = read_file(filepath)

    tokens = Lexer(source).tokens
    parser = Parser(tokens)
    program, errors = parser.parse()
    assert not errors
    assert program == expected_tree
