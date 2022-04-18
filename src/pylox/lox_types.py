from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Union

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    Protocol = object  # pragma: no cover

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter

String = str
Integer = int
Float = float
Boolean = bool


class LoxCallable(Protocol):
    def call(self, interpreter: Interpreter, arguments: list[LoxType]) -> LoxType:
        ...

    def arity(self) -> int:
        ...


class LoxObject(Protocol):
    def get(self, name: str) -> LoxType:
        ...

    def set(self, name: str, value: LoxType) -> None:
        ...


LoxType = Union[String, Integer, Float, Boolean, LoxCallable, LoxObject, None]
