from __future__ import annotations

from collections import Counter
from typing import Type

import pytest

from pylox.lexer import Lexer
from pylox.nodes import (
    Binary,
    ClassDef,
    FunctionDef,
    Grouping,
    Literal,
    Node,
    Print,
    Program,
    VarDeclaration,
    Variable,
)
from pylox.parser import Parser
from pylox.utils import walk


@pytest.mark.parametrize(
    ("source", "nodes"),
    (
        (
            """\
            class C {
                init() {
                    var x = 5;
                    print (x + 2);
                }
            }
            """,
            [
                Program,
                ClassDef,
                FunctionDef,
                VarDeclaration,
                Literal,
                Print,
                Grouping,
                Binary,
                Variable,
                Literal,
            ],
        ),
    ),
)
def test_walk(source: str, nodes: list[Type[Node]]) -> None:
    tokens = Lexer(source).tokens
    tree, errors = Parser(tokens).parse()
    assert not errors
    assert Counter(type(node) for node in walk(tree)) == Counter(nodes)
