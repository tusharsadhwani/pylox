from __future__ import annotations

import io
import os.path
from textwrap import dedent

import pytest
from pytest import CaptureFixture, MonkeyPatch

from pylox import main as pylox_main
from pylox.interpreter import Interpreter, InterpreterError
from pylox.lexer import Lexer
from pylox.parser import ParseError, Parser
from pylox.resolver import Resolver


@pytest.mark.parametrize(
    ("filename", "error"),
    (
        (
            "fail1.lox",
            """\
            Error in fail1.lox:3:20

                for (int i = 0; i < @; i++) {
                                    ^
            LexError: Unknown character found: '@'
            """,
        ),
        (
            "fail2.lox",
            """\
            Error in fail2.lox:1:6

                print "Hello!
                      ^
            LexError: Unterminated string
            """,
        ),
    ),
)
def test_lex_fail_files(filename: str, error: str, capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        test_dir = os.path.join(os.path.dirname(__file__), "testdata")
        filepath = os.path.join(test_dir, filename)
        pylox_main(argv=["pylox", filepath])

    stdout, _ = capsys.readouterr()
    assert stdout.rstrip() == dedent(error).rstrip()


@pytest.mark.parametrize(
    ("source", "error"),
    (
        ("class C < C {}", "A class cannot inherit from itself"),
        ("print this.x;", "Cannot use 'this' outside of a class"),
        ("print super.x;", "Cannot use 'super' outside of a class"),
        (
            "class C { foo() {print super.x;} }",
            "Cannot use 'super' in a class with no superclass",
        ),
    ),
)
def test_resolver_fail(source: str, error: str) -> None:
    with pytest.raises(ParseError) as exc:
        tokens = Lexer(source).tokens
        parser = Parser(tokens)
        tree, errors = parser.parse()
        assert not errors
        interpreter = Interpreter()
        resolver = Resolver(interpreter)
        resolver.visit(tree)

    assert exc.value.message == error


@pytest.mark.parametrize(
    ("filename", "error"),
    (
        (
            "fail3.lox",
            """\
            Error in fail3.lox:2:2

                i++;
                  ^
            ParseError: Unexpected token: '+'

            Error in fail3.lox:4:0

                ++j;
                ^
            ParseError: Unexpected token: '+'

            Found 2 errors.
            """,
        ),
        (
            "fail7.lox",
            """\
            Error in fail7.lox:3:6

                  var x = "y";
                      ^
            ParseError: Variable 'x' already defined in this scope
            """,
        ),
        (
            "fail8.lox",
            """\
            Error in fail8.lox:1:0

                return "global";
                ^
            ParseError: Cannot return outside of a function
            """,
        ),
    ),
)
def test_parse_fail_files(
    filename: str,
    error: str,
    capsys: CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        test_dir = os.path.join(os.path.dirname(__file__), "testdata")
        filepath = os.path.join(test_dir, filename)
        pylox_main(argv=["pylox", filepath])

    stdout, _ = capsys.readouterr()
    assert stdout.rstrip() == dedent(error).rstrip()


@pytest.mark.parametrize(
    ("source", "error"),
    (
        ("x;", "Undefined variable 'x'"),
        ("2 > '3';", "Unsupported types for '>': 'Number' and 'String'"),
        ("nil();", "'nil' object is not callable"),
        ("fun f(){} f.foo;", "Cannot access properties inside 'Function'"),
        ("class C {} C.foo = 5;", "Cannot set properties on 'Class'"),
        (
            "var x = true; class C < x {}",
            "Can only inherit from classes, found 'Boolean'",
        ),
    ),
)
def test_interpreter_fail(source: str, error: str) -> None:
    with pytest.raises(InterpreterError) as exc:
        tokens = Lexer(source).tokens
        parser = Parser(tokens)
        tree, errors = parser.parse()
        assert not errors
        interpreter = Interpreter()
        resolver = Resolver(interpreter)
        resolver.visit(tree)
        interpreter.visit(tree)

    assert exc.value.message == error


@pytest.mark.parametrize(
    ("filename", "error"),
    (
        (
            "fail4.lox",
            """\
            Error in fail4.lox:2:0

                y = x + 1;
                ^
            InterpreterError: Assigning to variable 'y' before declaration
            """,
        ),
        (
            "fail5.lox",
            """\
            Error in fail5.lox:2:2

                  x = "This variable doesn't exist";
                  ^
            InterpreterError: Assigning to variable 'x' before declaration
            """,
        ),
    ),
)
def test_interpret_fail_files(
    filename: str,
    error: str,
    capsys: CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        test_dir = os.path.join(os.path.dirname(__file__), "testdata")
        filepath = os.path.join(test_dir, filename)
        pylox_main(argv=["pylox", filepath])

    stdout, _ = capsys.readouterr()
    assert stdout.rstrip() == dedent(error).rstrip()


def test_run(capsys: CaptureFixture[str], monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["lox", "a.lox", "b.lox"])

    with pytest.raises(SystemExit):
        pylox_main()

    stdout, _ = capsys.readouterr()
    assert stdout == "Usage: lox [filename]\n"

    monkeypatch.setattr("sys.argv", ["lox"])
    monkeypatch.setattr("sys.stdin", io.StringIO("var x = 5;\nprint x;\nprint y;"))

    with pytest.raises(SystemExit):
        pylox_main()

    stdout, _ = capsys.readouterr()
    expected = dedent(
        """\
        > > 5.0
        > Error in <input>:1:6

            print y;
                  ^
        InterpreterError: Undefined variable 'y'
        >
        """
    )
    assert stdout.strip() == expected.strip()

    monkeypatch.setattr("sys.argv", ["lox", "tests/testdata/operators.lox"])
    with pytest.raises(SystemExit) as exc:
        pylox_main()

    assert exc.value.code == 0
