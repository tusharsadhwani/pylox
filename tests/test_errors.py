import os.path
from textwrap import dedent

import pytest
from pytest import CaptureFixture

from pylox import main as pylox_main


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
            Error in fail2.lox:3:27

                this is a multiline string.
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
