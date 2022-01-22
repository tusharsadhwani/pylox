from __future__ import annotations


class EnvironmentLookupError(Exception):
    ...


class Environment:
    def __init__(self) -> None:
        self._environment: dict[str, object] = {}

    def define(self, variable: str, value: object) -> None:
        # Note that this allows us to re-declare already declared variables.
        # We're allowing this, at global scope.
        self._environment[variable] = value

    def get(self, variable: str) -> object:
        try:
            return self._environment[variable]
        except KeyError:
            raise EnvironmentLookupError(f"Undefined variable {variable}")
