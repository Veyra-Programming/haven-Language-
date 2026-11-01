=============================================================================
Haven Programming Language (Heaven Language) — ODCS Edition
=============================================================================

Standard: Open Digital Continuity Standard (ODCS-1.0.0)
Specification & Architecture Author: Anirudha Puthraya
Language Runtime: Haven v1.0.0 (Production Core)

Haven is a modern, disruption-tolerant programming language engineered for sovereign,
local-first computing systems.

Key Capabilities:
-----------------
* Natural English Syntax (`set x to val`, `let x be val`, `repeat N times:`, `unless cond:`)
* First-Class Pipelining (`|>`, `_`, `into`)
* Hardware-Backed Durable Records (`durable record`)
* Cryptographic Continuity Ledgers (`checkpoint`, `verify`)
* Unified Developer Tooling (`haven run`, `haven eval`, `haven new`, `haven test`, `haven repl`)
* Haven AI SDK (`haven_ai`) with streaming & reasoning extraction

Quick Start:
------------
Launch the interactive REPL:

    haven repl

Run a script:

    haven run script.hvn

Run the test suite:

    haven test

Evaluate inline code:

    haven -c "set x to 42; print(x)"

For comprehensive documentation, see README.md and HAVEN_CLI_ODCS.md.
