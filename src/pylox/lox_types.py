from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Union

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter

String = str
Number = float
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


LoxType = Union[String, Number, Boolean, LoxCallable, LoxObject, None]
