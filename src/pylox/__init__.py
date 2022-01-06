"""pylox - A Lox interpreter written in Python."""
import sys
from typing import List, Optional

from .parser import Lexer, ParseError


def read_file(filename: str) -> str:
    with open(filename) as file:
        source = file.read()

    return source


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv

    if len(argv) > 2:
        print("Usage: pylox [filename]")
        return 1

    if len(argv) == 1:
        return run_interactive()

    filename = argv[1]
    source = read_file(filename)
    return run(source)


def run_interactive() -> int:
    while True:
        try:
            text = input("> ")
        except KeyboardInterrupt:
            return 1

        run(text)


def run(source: str) -> int:
    try:
        tokens = Lexer(source).tokens
        # TODO: parse
    except ParseError:
        return 1

    # TODO: run code

    return 0
