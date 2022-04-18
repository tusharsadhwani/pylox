# pylox

My first implementation of Lox, written in Python.

This implementation is actually a _superset_ of the Lox programming language
defined in the [Crafting Interpreters][1] book. Meaning,
every valid lox program will run on this interpreter too, but programs that
would throw an error in the book's implementation, might work in mine.

For example, this one supports single quotes:

```console
$ lox
> print 'Single quotes!';
Single quotes!
```

## Installation and usage

- Install via pip:

```console
pip install mypylox
```

- Run it interactively:

```console
$ lox
> print "Hi!";
Hi!
> var num = 2.5 + 2.5;
> print num;
5.0
```

- Run a file:

```console
$ cat myfile.lox
var name = "Tushar";
var age = "21";

print "My name is " + name + " and I'm " + age + " years old.";

$ lox myfile.lox
My name is Tushar and I'm 21 years old.
```

## Progress

What has already been implemented:

- [x] Entire lexer implementation
- [x] Expression parsing
- [x] Syntax Errors
- [x] Expression execution
- [x] Print statements
- [x] Variable declaration, and global scope
- [x] Interactive REPL
- [x] Variable assignment
- [x] Proper runtime errors
- [x] Synchronization and reporting multiple parse errors
- [x] Local scope, enclosing scope, blocks and nesting
- [x] `if`-`else` statements
- [x] `while` loops
- [x] `for` loops
- [x] Logical `and` and `or` operators
- [x] Function declarations, calls, first class functions and callbacks
- [x] Return values
- [x] Closures
- [x] Compile time variable resolution and binding
- [x] Class declarations, objects, and properties
- [x] Class properties
- [x] Methods
- [x] `this` attribute
- [x] Constructors
- [x] Inheritance

## Changes / Extra features

There's a small number of changes from the reference language:

- Defining a variable as itself inside a block does not result in a parse error.
  Instead, it uses the value from outer scope to define itself in local scope.
  This lets us simplify the resolver code: We don't need a separate `declare`
  and `define` method anymore, and each scope is a set, not a dictionary.

- You can access methods directly on a class, you don't need to necessarily
  create an object to do so. Doing this returns an "unbound method". The main
  reason to do this is for better DX, and to allow `dir(C)` to work. It is not
  yet decided if unbound methods are just not usable at all, or if some sort of
  binding mechanism will be implemented to allow for that. [TODO]

Here's the full set of extra features, and their progress:

- [x] _Much_ better error messages
- [x] Allowing single quotes for strings
- [x] String escapes: `\n`, `\t`, `\'`, `\"`, `\\` and `\↵`
- [x] New operators:
  - [x] Modulo `%`
  - [x] Integer division `\`
  - [x] Power `**`
- [ ] Augmented versions of all operators: `+=`, `**=`, etc.
- [ ] New data types:
  - [x] int: `42`
  - [ ] list: `[42, 56]`
  - [ ] dictionary: `{42: "Forty two"}`
- [ ] Indexing support: for lists, dictionaries and strings
- [ ] Comparison operators work on strings
- [ ] `break` and `continue` semantics in loops
- [ ] Exceptions, `try` / `except` blocks and `raise` statements
- [ ] Added builtin functions:
  - [ ] `input`
  - [ ] `format` (Python equivalent, for string interpolation)
  - [ ] `min`, `max` and `abs`
  - [ ] `map`, `filter` and `reduce` that take lists and return new lists
  - [x] `dir` to print out an object's attributes
- [ ] An `import` system
- [ ] A standard library
  - [ ] `random` module
  - [ ] `io` module string and binary reads/writes to files
  - [ ] `http` library to make a web server and client

Examples of all of these will be available in the [examples][2] folder.

## Ideas to tinker with

The following are ideas that I'm not 100% sure about, but would like to try.
Some of these will not be compatible with the original lox language, so if I
implement those, I'll do that in a separate branch.

- No `nil`. Variables will always have to be initialized with a value, and
  functions will either never return anything, or return in every case. This
  will be checked at compile time.
- Declaration scope vs. Block scope. The idea being, if we don't allow `nil`,
  block scope might cause an issue, but no `nil` + declaration scope might work.
- Adding whitespace tokens to the lexer and AST, and adding a code formatting
  module into the standard library.
- Built-in benchmarking library.

## Testing / Development

Get the project:

```bash
git clone https://github.com/tusharsadhwani/pylox
cd pylox
```

Get the dev requirements:

```console
pip install -r requirements-dev.txt
```

Run tests:

```console
pytest
```

Type check the code:

```console
mypy .
```

[1]: https://craftinginterpreters.com
[2]: https://github.com/tusharsadhwani/pylox/tree/master/examples
