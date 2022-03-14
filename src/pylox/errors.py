from __future__ import annotations


class LoxError(Exception):
    def __init__(self, message: str, index: int) -> None:
        super().__init__(message)
        self.message = message
        self.index = index
