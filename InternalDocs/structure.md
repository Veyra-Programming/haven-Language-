# Haven Source Code & Architecture

This section gives an overview of Haven Language's code structure and provides a summary of file locations for language subsystems, core modules, and ODCS/OFCS built-ins.

Standard Architecture & Specification by **Anirudha Puthraya**.

---

## Source Code Layout

### 1. Standard Library & Continuity Subsystems
For a Haven module or subsystem, the typical layout is:
* `Lib/haven/<module>.py` — Core Haven standard library, backend framework, and enterprise annotations.
* `Lib/odcs/<module>.py` — Open Digital Continuity Standard (ODCS) CRDTs, Merkle DAG, mesh, and telemetry.
* `Lib/ofcs/<module>.py` — Open Financial Continuity Standard (OFCS) high-precision money, ledger, and reconciliation.
* `Modules/_<module>.c` — High-speed C accelerator extension module.
* `tests/test_<module>.hvn` — Native Haven test suite executed via `haven test`.

### 2. Extension Modules
For native C extension modules:
* `Modules/<module>module.c`
* `tests/test_<module>.hvn`
* `Doc/library/<module>.rst`

### 3. Builtin Objects & Memory Model
For built-in types:
* `Objects/<builtin>object.c`
* `Lib/test/test_<builtin>.py`
* `Doc/builtins/stdtypes.rst`

Key core types:
* Built-in type `int`: [`Objects/longobject.c`](../Objects/longobject.c)
* Built-in type `str`: [`Objects/unicodeobject.c`](../Objects/unicodeobject.c)
* Built-in type `tuple`: [`Objects/tupleobject.c`](../Objects/tupleobject.c)
* Built-in type `dict`: [`Objects/dictobject.c`](../Objects/dictobject.c)

### 4. Haven Grammar & Parser Architecture
* [`Grammar/haven.gram`](../Grammar/haven.gram) & [`Grammar/python.gram`](../Grammar/python.gram) — Formal PEG grammar definitions for natural-English syntax (`set`, `let`, `remember`, `increase`, `decrease`, `whenever`, `unless`, `until`, `repeat`, `give back`, `forever`, `durable record`, `checkpoint`).
* [`Parser/parser.c`](../Parser/parser.c) — Generated deterministic recursive-descent parser.
* [`Parser/action_helpers.c`](../Parser/action_helpers.c) — AST constructor actions and keyword mappings.

### 5. Haven Virtual Machine & Execution Engine
* [`Python/ceval.c`](../Python/ceval.c) — Main bytecode dispatch loop.
* [`Python/compile.c`](../Python/compile.c) — AST to bytecode compiler.
* [`Python/bltinmodule.c`](../Python/bltinmodule.c) — Native built-in functions.
* [`Python/sysmodule.c`](../Python/sysmodule.c) — System state and Haven runtime introspection.
* [`PCbuild/amd64/haven.exe`](../PCbuild/amd64/haven.exe) — Native Windows binary executable.
* [`haven.bat`](../haven.bat) — Haven CLI entry-point launcher.
