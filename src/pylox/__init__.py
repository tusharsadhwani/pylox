"""pylox - A Lox interpreter written in Python."""
from __future__ import annotations

import argparse
import os.path
import traceback
from typing import Sequence

from pylox.errors import LoxError
from pylox.interpreter import Interpreter, InterpreterError
from pylox.lexer import Lexer, LexError, LexIncompleteError
from pylox.nodes import ExprStmt
from pylox.parser import ParseEOFError, ParseError, Parser
from pylox.resolver import Resolver
from pylox.utils import get_snippet_line_col


def read_file(filename: str) -> str:
    with open(filename) as file:
        source = file.read()

    return source


class PyloxArgs(argparse.Namespace):
    debug: bool
    interactive: bool
    filename: str


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run pylox in interactive mode",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print a stack trace when a crash occurs",
    )
    parser.add_argument("filename", help="Name of file to run", nargs="?")
    args = parser.parse_args(argv, namespace=PyloxArgs())

    if args.filename is None:
        raise SystemExit(run_interactive(args.debug))

    if args.interactive:
        interpreter = Interpreter()
        run(args.filename, args.debug, interpreter)
        raise SystemExit(run_interactive(args.debug, interpreter))

    raise SystemExit(run(args.filename, args.debug))


def run_interactive(
    debug: bool = False,
    interpreter: Interpreter | None = None,
) -> int:
    if interpreter is None:
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
        except KeyboardInterrupt:  # pragma: no cover -- dunno how to test this.
            print(" -- Cancelled")
            lines = []
        except InterpreterError as exc:
            pretty_print_error(code, "<input>", exc)
        except Exception as exc:
            print_exception(exc, debug=debug)


def run(
    filepath: str,
    debug: bool = False,
    interpreter: Interpreter | None = None,
) -> int:
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

    if interpreter is None:
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
    except Exception as exc:
        print_exception(exc, debug=debug)

    return 0


def print_exception(exc: Exception, debug: bool = False) -> None:
    if debug:
        traceback.print_exc()
    else:
        error_name = exc.__class__.__name__
        print("Internal Error:")
        print(f"{error_name}: {exc}")
        print("Use the --debug flag to generate a stack trace.")


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
