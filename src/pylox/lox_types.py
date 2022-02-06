from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Union

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter

String = str
Number = float
Boolean = bool


class Callable(Protocol):
    def call(self, interpreter: Interpreter, arguments: list[LoxType]) -> LoxType:
        ...

    def arity(self) -> int:
        ...


LoxType = Union[String, Number, Boolean, Callable, None]
