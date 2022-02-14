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
        if variable not in self._environment:
            raise EnvironmentLookupError(
                f"Assigning to variable {variable!r} before declaration"
            )

        self._environment[variable] = value

    def get(self, variable: str) -> LoxType:
        if variable not in self._environment:
            raise EnvironmentLookupError(f"Undefined variable {variable!r}")

        return self._environment[variable]

    def ancestor(self, depth: int) -> Environment:
        environment = self
        for _ in range(depth):
            assert environment.enclosing is not None
            environment = environment.enclosing

        return environment

    def assign_at(self, depth: int, name: str, value: LoxType) -> None:
        return self.ancestor(depth).define(name, value)

    def get_at(self, depth: int, name: str) -> LoxType:
        return self.ancestor(depth).get(name)
