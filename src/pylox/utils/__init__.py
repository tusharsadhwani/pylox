from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Generator, Iterable

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

from attr import asdict

from pylox.lox_types import Boolean, Float, Integer, LoxCallable, LoxType, String
from pylox.nodes import Node


def get_snippet_line_col(source: str, index: int) -> tuple[int, int, str]:
    """Returns line number, column number and line of code at the given index."""
    line, col = 1, 0

    current = 0
    snippet_start_index = 0
    for char in source:
        if current == index:
            break

        if char == "\n":
            snippet_start_index = current + 1
            line += 1
            col = 0
        else:
            col += 1

        current += 1

    while current < len(source) and source[current] != "\n":
        current += 1

    snippet_end_index = current
    snippet = source[snippet_start_index:snippet_end_index]
    return line, col, snippet


def get_lox_type_name(value: LoxType) -> str:
    from pylox.interpreter import LoxClass, LoxFunction

    if value is None:
        return "nil"

    if isinstance(value, bool):
        return "Boolean"

    if isinstance(value, String):
        return "String"

    if isinstance(value, Integer):
        return "Integer"

    if isinstance(value, Float):
        return "Float"

    if isinstance(value, LoxFunction):
        return "Function"

    if isinstance(value, LoxClass):
        return "Class"

    raise NotImplementedError(f"Unknown type for value: {value}")


def is_lox_callable(value: LoxType) -> TypeGuard[LoxCallable]:
    return callable(getattr(value, "call", None))


def is_truthy(value: LoxType) -> bool:
    if value is None:
        return False

    if isinstance(value, (String, Integer, Float, Boolean)):
        return bool(value)

    raise NotImplementedError(
        f"Truthiness not implemented for {get_lox_type_name(value)}"
    )


def attrs_fields(node: Node) -> Generator[Node, None, None]:
    """Yield attrs fields from an attrs object"""
    for field_name in asdict(node).keys():
        yield getattr(node, field_name)


def iter_children(node: Node) -> Generator[Node, None, None]:
    """
    Yield all direct child nodes of `node`, that is, all fields that are nodes
    and all items of fields that are lists of nodes.
    """
    for field in attrs_fields(node):
        if isinstance(field, Node):
            yield field
        elif isinstance(field, Iterable):
            for item in field:
                if isinstance(item, Node):
                    yield item


def walk(node: Node) -> Generator[Node, None, None]:
    """
    Recursively yield all descendant nodes in the tree starting at `node`
    (including `node` itself), in no specified order.
    """
    nodes = deque([node])
    while nodes:
        node = nodes.popleft()
        nodes.extend(iter_children(node))
        yield node
