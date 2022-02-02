from __future__ import annotations

from pylox.lox_types import LoxType


class EnvironmentLookupError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class Environment:
    def __init__(self, enclosing: Environment | None = None) -> None:
        self._environment: dict[str, LoxType] = {}
        self.enclosing = enclosing

    def define(self, variable: str, value: LoxType) -> None:
        # Note that this allows us to re-declare already declared variables.
        # We're allowing this, at global scope.
        self._environment[variable] = value

    def assign(self, variable: str, value: LoxType) -> None:
        if variable in self._environment:
            self._environment[variable] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(variable, value)
            return

        # So this will only be raised when enclosing is None,
        # i.e. when variable is not found even in the global scope.
        raise EnvironmentLookupError(
            f"Assigning to variable {variable!r} before declaration"
        )

    def get(self, variable: str) -> LoxType:
        if variable in self._environment:
            return self._environment[variable]

        if self.enclosing is not None:
            return self.enclosing.get(variable)

        raise EnvironmentLookupError(f"Undefined variable {variable!r}")
