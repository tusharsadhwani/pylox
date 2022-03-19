"""pylox - A Lox interpreter written in Python."""
from __future__ import annotations

import os.path
import sys
from typing import Sequence

from pylox.errors import LoxError
from pylox.interpreter import Interpreter, InterpreterError
from pylox.lexer import Lexer, LexError, LexIncompleteError
from pylox.nodes import ExprStmt
from pylox.parser import ParseEOFError, ParseError, Parser
from pylox.resolver import Resolver


def read_file(filename: str) -> str:
    with open(filename) as file:
        source = file.read()

    return source


def get_snippet_line_col(source: str, index: int) -> tuple[int, int, str]:
    """Returns line number, column number and line of code at the given index."""
    line, col = 1, 0

    current = 0
    snippet_start_index = 0
    for char in source:
        if current == index:
            break

        if char == "\n":
            snippet_start_index = current + 1
            line += 1
            col = 0
        else:
            col += 1

        current += 1

    while current < len(source) and source[current] != "\n":
        current += 1

    snippet_end_index = current
    snippet = source[snippet_start_index:snippet_end_index]
    return line, col, snippet


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv

    if len(argv) > 2:
        print("Usage: lox [filename]")
        raise SystemExit(1)

    if len(argv) == 1:
        raise SystemExit(run_interactive())

    filepath = argv[1]
    raise SystemExit(run(filepath))


def run_interactive() -> int:  # pragma: no cover
    interpreter = Interpreter()
    lines: list[str] = []
    while True:
        try:
            line = input("... " if lines else "> ")
            lines.append(line)
        except EOFError:
            # Close REPL
            return 0
        except KeyboardInterrupt:
            print()
            # Clear the stored lines
            lines = []

        code = "\n".join(lines)

        try:
            tokens = Lexer(code).tokens
            parser = Parser(tokens)
            tree = parser.parse(mode="repl")
            resolver = Resolver(interpreter)
            resolver.visit(tree)
            lines = []
        except LexIncompleteError:
            # Incomplete string
            continue
        except LexError as exc:
            pretty_print_error(code, "<input>", exc)
            lines = []
            continue
        except ParseEOFError:
            # Incomplete command
            continue
        except ParseError as exc:
            pretty_print_error(code, "<input>", exc)
            lines = []
            continue

        try:
            # If the program is a single expression, print its output
            if len(tree.body) == 1 and isinstance(tree.body[0], ExprStmt):
                expression = tree.body[0].expression
                output = interpreter.evaluate(expression)
                if output is not None:
                    if output is True:
                        print("true")
                    elif output is False:
                        print("false")
                    else:
                        print(output)
            else:
                interpreter.visit(tree)
        except KeyboardInterrupt:
            print("\rCancelled")
            lines = []
        except InterpreterError as exc:
            pretty_print_error(code, "<input>", exc)


def run(filepath: str) -> int:
    source = read_file(filepath)
    filename = os.path.basename(filepath)
    try:
        tokens = Lexer(source).tokens
    except LexError as exc:
        pretty_print_error(source, filename, exc)
        return 1

    parser = Parser(tokens)
    tree, errors = parser.parse()
    if errors:
        if len(errors) > 1:
            pretty_print_errors(source, filename, errors)
        else:
            pretty_print_error(source, filename, errors[0])
        return 1

    interpreter = Interpreter()

    resolver = Resolver(interpreter)
    try:
        resolver.visit(tree)
    except ParseError as exc:
        pretty_print_error(source, filename, exc)
        return 1

    try:
        interpreter.visit(tree)
    except InterpreterError as exc:
        pretty_print_error(source, filename, exc)
        return 1

    return 0


def pretty_print_errors(source: str, filename: str, errors: Sequence[LoxError]) -> None:
    for error in errors:
        pretty_print_error(source, filename, error)
        print()

    print(f"Found {len(errors)} errors.")


def pretty_print_error(source: str, filename: str, exc: LoxError) -> None:
    line, col, snippet = get_snippet_line_col(source, exc.index)
    print(f"Error in {filename}:{line}:{col}")

    indent = "    "
    print()
    print(indent + snippet)
    print(indent + "^".rjust(col + 1))
    print(f"{exc.__class__.__name__}: {exc.message}")


# TODO: Document the entire codebase :(
# TODO: Move all the ugly if chains to match statements when
# python 3.10 becomes the minimum supported version
