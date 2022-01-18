# pylox

My first implementation of Lox, written in Python.

## Design decisions

It'll be a reference implementation, except for a few additions:

- New data types: lists and dictionaries
- Allowing single quotes for strings
- Modulo `%` and power `**` operators
- Comparison operators for strings
- _Much_ better error messages
- `try` / `except`
- An import system
- An actual standard library
  - Can start with a `math` and a `random` module

## Ideas to tinker with

The following are ideas that I'm not 100% sure about, but would like to try:

- No `nil`
- Function scope vs. Block scope. The idea being, if we don't allow `nil`,
  block scope might cause an issue, but no `nil` + function scope might work.
- Adding whitespace tokens to the parser and AST, and adding a code formatting
  module into the standard library.
