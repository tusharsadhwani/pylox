from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing_extensions import TypeGuard

from pylox.lox_types import Boolean, Callable, LoxType, Number, String


def get_lox_type_name(value: LoxType) -> str:
    if value is None:
        return "nil"

    if isinstance(value, bool):
        return "Boolean"

    if isinstance(value, String):
        return "String"

    if isinstance(value, Number):
        return "Number"

    if is_lox_callable(value):
        return "Callable"

    raise NotImplementedError(f"Unknown type for value: {value}")


def is_lox_callable(value: LoxType) -> TypeGuard[Callable]:
    return callable(getattr(value, "call", None))


def is_truthy(value: LoxType) -> bool:
    if value is None:
        return False

    if isinstance(value, (String, Number, Boolean)):
        return bool(value)

    type_name = get_lox_type_name(value)
    raise NotImplementedError(f"Truthiness not implemented for {type_name}")
