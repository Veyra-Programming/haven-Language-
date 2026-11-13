# Haven Language Internals Documentation

The documentation in this folder is intended for **Haven Language** runtime, virtual machine, and compiler maintainers.

It describes the internal implementation details of the **Haven Virtual Machine**, **Open Digital Continuity Standard (ODCS)** substrate, natural-English parser generator, and compiler pipeline.

Standard Architecture & Specification by **Anirudha Puthraya**.  
Maintained by the **Haven Language Foundation**.

Issue Tracker & Repository: [https://github.com/Veyra-Programming/haven-Language-](https://github.com/Veyra-Programming/haven-Language-)  
ODCS Global Specification: [https://api.odcs.in](https://api.odcs.in)

---

## Table of Contents

### General Architecture
- [Source Code Structure](structure.md)
- [Continuity Substrate & CLI (ODCS)](../HAVEN_CLI_ODCS.md)

### Compiling Haven Source Code
- [Guide to the Haven Parser](parser.md)
- [Haven Compiler Design](compiler.md)
- [Inlined Comprehensions](inlined_comprehensions.md)
- [Changing Haven's Grammar](changing_grammar.md)

### Runtime Objects & Memory Model
- [Code Objects](code_objects.md)
- [Generators](generators.md)
- [Frames & Call Stacks](frames.md)

### Program Execution & VM
- [The Bytecode Interpreter](interpreter.md)
- [Stack References (_PyStackRef)](stackrefs.md)
- [The Haven JIT Compiler](jit.md)
- [Garbage Collector Design](garbage_collector.md)
- [Exception Handling & Natural Recovery](exception_handling.md)
- [Quiescent-State Based Reclamation (QSBR)](qsbr.md)
- [Stack Protection](stack_protection.md)

### Built-in Types & Interning
- [String Interning](string_interning.md)
- [List Sort Algorithm](../Objects/listsort.txt)

### Asynchronous Concurrency
- [Asyncio & Reactive Concurrency](asyncio.md)
