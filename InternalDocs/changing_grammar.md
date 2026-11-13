# Changing Haven Language's Grammar

There is more to extending or changing Haven's grammar than simply editing
[`Grammar/haven.gram`](../Grammar/haven.gram) or [`Grammar/python.gram`](../Grammar/python.gram).
Below is a checklist of components and build steps required when introducing new syntax.

Standard Architecture & Specification by **Anirudha Puthraya**.

> [!NOTE]
> Many grammar modifications require re-generating derived parser files and rebuilding the runtime. On Windows, use `PCbuild\build.bat` or `build.bat --regen`.

---

## Grammar Checklist

* [`Grammar/haven.gram`](../Grammar/haven.gram) & [`Grammar/python.gram`](../Grammar/python.gram):
  The PEG grammar definitions, with actions that construct AST nodes. Specialized syntax error rules
  (`invalid_*` rules) reside in [`Grammar/invalid.gram`](../Grammar/invalid.gram).
  After changing grammar rules, run `build.bat --regen` on Windows (or `make regen-pegen` on Unix)
  to regenerate [`Parser/parser.c`](../Parser/parser.c) and [`Parser/parser_invalid.c`](../Parser/parser_invalid.c)
  using Haven's PEG parser generator.

* [`Parser/action_helpers.c`](../Parser/action_helpers.c):
  Contains C helper routines called by PEG semantic actions when mapping keywords to AST statements
  (e.g., mapping `increase <target> by <val>` to augmented assignment or `give back <expr>` to return statements).

* [`Grammar/Tokens`](../Grammar/Tokens):
  The master list of lexical token types. After adding a token, run `build.bat --regen` (or `make regen-token`)
  to update [`Include/internal/pycore_token.h`](../Include/internal/pycore_token.h),
  [`Parser/token.c`](../Parser/token.c), and [`Lib/token.py`](../Lib/token.py).

* [`Parser/Python.asdl`](../Parser/Python.asdl):
  The Abstract Syntax Description Language definition. Defines AST node structures.
  Regenerated via `make regen-ast` into [`Include/internal/pycore_ast.h`](../Include/internal/pycore_ast.h)
  and [`Python/Python-ast.c`](../Python/Python-ast.c).

* [`Parser/lexer/`](../Parser/lexer):
  Contains the Haven tokenizer and lexical analysis engine.

* [`Python/ast.c`](../Python/ast.c):
  Validates AST node structures and invariant relationships.

* [`Python/ast_unparse.c`](../Python/ast_unparse.c):
  Reconstructs source strings from AST trees.

* [`Python/compile.c`](../Python/compile.c):
  Translates AST nodes into bytecode instructions executed by the Haven Virtual Machine.

* [`Lib/keyword.py`](../Lib/keyword.py):
  Exposes the official set of recognized Haven language keywords (`kwlist`).

* `tests/`:
  Always write verification test files in `tests/test_<feature>.hvn` exercising the new syntax,
  and verify that `haven test` runs 100% green.
