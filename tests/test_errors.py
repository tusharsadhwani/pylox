from __future__ import annotations

import io
import os.path
import re
from textwrap import dedent

import pytest
from pytest import CaptureFixture, MonkeyPatch

from pylox import main as pylox_main
from pylox import run_interactive
from pylox.interpreter import Interpreter, InterpreterError
from pylox.lexer import Lexer, LexError
from pylox.parser import ParseError, Parser
from pylox.resolver import Resolver


def test_file_not_found(capsys: CaptureFixture[str]) -> None:
    """Tests the error message when a wrong path is passed to pylox."""
    with pytest.raises(SystemExit):
        pylox_main(argv=["nonexistent_file.py"])

    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    assert stdout == "Error: given path does not exist\n"

    with pytest.raises(SystemExit):
        pylox_main(argv=["tests"])

    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    assert stdout == "Error: given path is a directory\n"


@pytest.mark.parametrize(
    ("source", "error"),
    ((r'"a\b"', r"Unknown escape sequence: '\b'"),),
)
def test_lex_fail(source: str, error: str) -> None:
    with pytest.raises(LexError) as exc:
        Lexer(source)

    assert exc.value.message == error


@pytest.mark.parametrize(
    ("filename", "error"),
    (
        (
            "fail1.lox",
            """\
            Error in fail1.lox:3:20

                And it has \\na few \\escapes.
                                    ^
            LexError: Unknown escape sequence: '\\e'
            """,
        ),
        (
            "fail2.lox",
            """\
            Error in fail2.lox:1:6

                print "Hello!
                      ^
            LexIncompleteError: Unterminated string
            """,
        ),
    ),
)
def test_lex_fail_files(filename: str, error: str, capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        test_dir = os.path.join(os.path.dirname(__file__), "testdata")
        filepath = os.path.join(test_dir, filename)
        pylox_main(argv=[filepath])

    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    assert stdout.rstrip() == dedent(error).rstrip()


@pytest.mark.parametrize(
    ("source", "error"),
    (
        ("if (2 >", "Unexpected end of file while parsing"),
        ("super.", "Expected to find method name, found EOF"),
        ("class 5 {}", "Expected to find class name, found '5'"),
    ),
)
def test_parse_fail(source: str, error: str) -> None:
    tokens = Lexer(source).tokens

    with pytest.raises(ParseError) as exc:
        Parser(tokens).parse(mode="repl")

    assert exc.value.message == error


@pytest.mark.parametrize(
    ("source", "error"),
    (
        ("class C < C {}", "A class cannot inherit from itself"),
        ("return 'global';", "Cannot return outside of a function"),
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
            Error in fail8.lox:1:5

                fun f(
                     ^
            ParseError: More than 255 parameters not allowed in a function definition

            Error in fail8.lox:14:4

                f() = 10;
                    ^
            ParseError: Invalid assign target: 'Call'

            Error in fail8.lox:16:9

                value = f(
                         ^
            ParseError: More than 255 arguments not allowed in a function call
            
            Found 3 errors.
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
        pylox_main(argv=[filepath])

    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    assert stdout.rstrip() == dedent(error).rstrip()


@pytest.mark.parametrize(
    ("source", "error"),
    (
        ("x;", "Undefined variable 'x'"),
        ("print -true;", "Expected 'Integer' or 'Float' for unary '-', got 'Boolean'"),
        ("2 > '3';", "Unsupported types for '>': 'Integer' and 'String'"),
        ("nil();", "'nil' object is not callable"),
        ("fun f(){} f.foo;", "Cannot access properties inside 'Function'"),
        ("class C {} C.foo = 5;", "Cannot set properties on 'Class'"),
        (
            "var x = true; class C < x {}",
            "Can only inherit from classes, found 'Boolean'",
        ),
        ("class C {} var c = C(); c.foo();", "'C' object has no attribute 'foo'"),
        ("print 3 / 0;", "Division by zero"),
        ("fun f(a) {print a;} f();", "<function 'f'> expected 1 arguments, got 0"),
        ("class C {init(a, b) {}} C(10);", "<class 'C'> expected 2 arguments, got 1"),
        ("dir(5.5);", "dir() can only be used on classes and objects, not 'Float'"),
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
        pylox_main(argv=[filepath])

    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    assert stdout.rstrip() == dedent(error).rstrip()


def test_run(capsys: CaptureFixture[str], monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["lox", "a.lox", "b.lox"])

    with pytest.raises(SystemExit):
        pylox_main()

    stdout, stderr = capsys.readouterr()
    assert stderr == (
        "usage: lox [-h] [-i] [--debug] [filename]\n"
        "lox: error: unrecognized arguments: b.lox\n"
    )
    assert stdout == ""

    monkeypatch.setattr("sys.argv", ["lox"])
    monkeypatch.setattr("sys.stdin", io.StringIO("var x = 5;\nprint x;\nprint y;"))

    with pytest.raises(SystemExit):
        pylox_main()

    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    expected = dedent(
        """\
        > > 5
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

    capsys.readouterr()  # to flush the output
    assert exc.value.code == 0

    monkeypatch.setattr("sys.argv", ["lox", "tests/testdata/fail9.lox"])
    with pytest.raises(SystemExit) as exc:
        pylox_main()

    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    expected = dedent(
        """\
        Internal Error:
        RecursionError: maximum recursion depth exceeded(.*)
        Use the --debug flag to generate a stack trace.
        """
    )
    assert re.fullmatch(expected.strip(), stdout.strip()) is not None

    monkeypatch.setattr("sys.argv", ["lox", "tests/testdata/fail9.lox", "--debug"])
    with pytest.raises(SystemExit) as exc:
        pylox_main()

    stdout, stderr = capsys.readouterr()
    assert stdout == ""

    output = stderr.splitlines()
    assert len(output) > 1000
    assert output[-1].startswith("RecursionError: maximum recursion depth exceeded")


def test_interactive_flag(
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.argv", ["lox", "-i", "tests/testdata/simple.lox"])
    monkeypatch.setattr("sys.stdin", io.StringIO("print !a;"))

    with pytest.raises(SystemExit):
        pylox_main()

    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    expected = dedent(
        """\
        Hello
        5
        false
        27.0
        > true
        >
        """
    )
    assert stdout.strip() == expected.strip()


def test_run_interactive(capsys: CaptureFixture[str], monkeypatch: MonkeyPatch) -> None:
    input_counter = 0
    lines = [
        "var x = (",
        "",  # Supposed to test Ctrl+C behaviour here. See below.
        "var x = 5;",
        "print x;",
        "print '",
        "abc';",
        "print '\\",
        "def';",
        "@",
        "return;",
        "true;",
        "false;",
        "2 + 2;",
    ]

    def fake_input(prompt: str = "") -> str:
        print(prompt, end="")
        nonlocal input_counter

        # After lines end, just raise EOFError
        if input_counter == len(lines):
            raise EOFError

        # For line 2, emulate Ctrl+C
        if input_counter == 1:
            input_counter += 1
            raise KeyboardInterrupt

        line = lines[input_counter]
        input_counter += 1

        # This emulates user input showing up on terminal
        print(line)

        return line

    monkeypatch.setattr("builtins.input", fake_input)
    run_interactive()

    stdout, stderr = capsys.readouterr()
    assert stderr == ""

    expected = """\
    > var x = (
    ... 
    > var x = 5;
    > print x;
    5
    > print '
    ... abc';

    abc
    > print '\\
    ... def';
    def
    > @
    Error in <input>:1:0

        @
        ^
    LexError: Unknown character found: '@'
    > return;
    Error in <input>:1:0

        return;
        ^
    ParseError: Cannot return outside of a function
    > true;
    true
    > false;
    false
    > 2 + 2;
    4
    > 
    """
    assert stdout.rstrip() == dedent(expected).rstrip()


def test_crash_handling(capsys: CaptureFixture[str], monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("fun f() { f(); } f();\nprint 10;"))
    run_interactive()

    stdout, stderr = capsys.readouterr()
    assert stderr == ""

    expected = """\
        > Internal Error:
        RecursionError: maximum recursion depth exceeded while calling a Python object
        Use the --debug flag to generate a stack trace.
        > 10
        >
    """
    assert stdout.rstrip() == dedent(expected).rstrip()
