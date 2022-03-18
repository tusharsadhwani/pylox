from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Generator, Iterable

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

from attr import asdict

from pylox.lox_types import Boolean, LoxCallable, LoxType, Number, String
from pylox.nodes import Node


def get_lox_type_name(value: LoxType) -> str:
    from pylox.interpreter import LoxClass, LoxFunction

    if value is None:
        return "nil"

    if isinstance(value, bool):
        return "Boolean"

    if isinstance(value, String):
        return "String"

    if isinstance(value, Number):
        return "Number"

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

    if isinstance(value, (String, Number, Boolean)):
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
