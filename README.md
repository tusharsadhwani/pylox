# pylox

My first implementation of Lox, written in Python.

## Design decisions

It'll be a reference implementation, except for a few additions:

- Allowing single quotes
- Modulo operator
- _Much_ better error messages
- An actual standard library, and import system

## Ideas to tinker with

The following are ideas that I'm not 100% sure about, but would like to try:

- No `nil`
- Function scope vs. Block scope. The idea being, if we don't allow `nil`,
  block scope might cause an issue, but no `nil` + function scope might work.
- Adding whitespace tokens to the parser and AST, and adding a code formatting
  module into the standard library.
