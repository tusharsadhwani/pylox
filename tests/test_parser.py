import os

import pytest

from pylox.lexer import Lexer
from pylox.nodes import (
    Assignment,
    Binary,
    Block,
    ExprStmt,
    Grouping,
    Literal,
    Print,
    Program,
    VarDeclaration,
    Variable,
)
from pylox.parser import Parser
from pylox.tokens import EOF, Token, TokenType
from pylox.utils.ast_printer import AstPrinter


def read_file(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


@pytest.mark.parametrize(
    ("tokens", "expected_tree"),
    (
        ([Token(TokenType.IDENTIFIER, "abc"), EOF], "abc"),
        ([Token(TokenType.NIL, "nil"), EOF], "nil"),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "1", 1),
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
                Token(TokenType.NUMBER, "2", 2),
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
                Token(TokenType.NUMBER, "2", 2.0),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "3", 3.0),
                Token(TokenType.BANG_EQUAL, "!="),
                Token(TokenType.NUMBER, "10", 10.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.BANG_EQUAL, "!="),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "1", 1.0),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "3", 3.0),
                Token(TokenType.GREATER, ">"),
                Token(TokenType.NUMBER, "5", 5.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.RIGHT_PAREN, ")"),
                EOF,
            ],
            """
            (((x == y) == true) == 
                (group
                    ((group ((2.0 + 3.0) != 10.0))
                    !=
                    (group ((1.0 + 3.0) > 5.0)))))
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
                Token(TokenType.NUMBER, "5", 5.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.EQUAL_EQUAL, "=="),
                Token(TokenType.IDENTIFIER, "fibonacci"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "4", 4.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.IDENTIFIER, "fibonacci"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "3", 3.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                EOF,
            ],
            "((fibonacci 5.0) == ((fibonacci 4.0) + (fibonacci 3.0)))",
        ),
        (
            [
                Token(TokenType.IDENTIFIER, "a"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "10", 10.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "20", 20.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                Token(TokenType.LEFT_PAREN, "("),
                Token(TokenType.NUMBER, "30", 30.0),
                Token(TokenType.RIGHT_PAREN, ")"),
                EOF,
            ],
            "(((a 10.0) 20.0) 30.0)",
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
            "(2.0 + (3.0 * 5.0))",
        ),
        (
            "expression_long.lox",
            """
            ((group
                ((((2.0 > 3.0) > (4.0 + 5.0)) != x) == ((y * z) / w)))
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
                Token(TokenType.EQUAL, "="),
                Token(TokenType.NUMBER, "5", 5.0),
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
                Token(TokenType.NUMBER, "2", 2.0),
                Token(TokenType.PLUS, "+"),
                Token(TokenType.NUMBER, "3", 3.0),
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
                                    left=Literal(2.0),
                                    operator=Token(TokenType.PLUS, "+"),
                                    right=Literal(3.0),
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
                Token(TokenType.NUMBER, "5", 5),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.LEFT_BRACE, "{"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.NUMBER, "10", 10),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.LEFT_BRACE, "{"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.NUMBER, "20", 20),
                Token(TokenType.SEMICOLON, ";"),
                Token(TokenType.RIGHT_BRACE, "}"),
                Token(TokenType.RIGHT_BRACE, "}"),
                Token(TokenType.VAR, "var"),
                Token(TokenType.IDENTIFIER, "x"),
                Token(TokenType.EQUAL, "="),
                Token(TokenType.NUMBER, "40", 40),
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
        )
        # TODO: add more tests
    ),
)
def test_parser(tokens: list[Token], expected_tree: Program) -> None:
    parser = Parser(tokens)
    program, errors = parser.parse()
    assert program == expected_tree
    assert errors == []


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
                        initializer=Literal(5.0, index=23),
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
                                            left=Literal(3.0, index=74),
                                            operator=Token(
                                                TokenType.PLUS, "+", index=76
                                            ),
                                            right=Literal(5.0, index=78),
                                            index=74,
                                        ),
                                        index=73,
                                    ),
                                    index=66,
                                ),
                                operator=Token(TokenType.SLASH, "/", index=81),
                                right=Literal(2.0, index=83),
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
    assert program == expected_tree
    assert errors == []


# TODO: add failing tests
