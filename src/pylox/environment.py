from __future__ import annotations


class EnvironmentLookupError(Exception):
    ...


class Environment:
    def __init__(self, enclosing: Environment | None = None) -> None:
        self._environment: dict[str, object] = {}
        self.enclosing = enclosing

    def define(self, variable: str, value: object) -> None:
        # Note that this allows us to re-declare already declared variables.
        # We're allowing this, at global scope.
        self._environment[variable] = value

    def assign(self, variable: str, value: object) -> None:
        if variable in self._environment:
            self._environment[variable] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(variable, value)
            return

        # So this will only be raised when enclosing is None,
        # i.e. when variable is not found even in the global scope.
        raise EnvironmentLookupError(f"Undefined variable {variable!r}")

    def get(self, variable: str) -> object:
        if variable in self._environment:
            return self._environment[variable]

        if self.enclosing is not None:
            return self.enclosing.get(variable)

        raise EnvironmentLookupError(f"Undefined variable {variable!r}")
