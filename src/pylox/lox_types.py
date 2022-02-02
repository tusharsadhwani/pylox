from __future__ import annotations

from typing import Protocol, Union

String = str
Number = float
Boolean = bool


class Callable(Protocol):
    def call(self) -> LoxType:
        ...

    def arity(self) -> int:
        ...


LoxType = Union[String, Number, Boolean, Callable, None]
