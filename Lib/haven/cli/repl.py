"""
Haven Language Interactive REPL (Read-Eval-Print Loop)
With native syntax evaluation, live ODCS ledger inspection, benchmarking, and developer tools.
Standard Specification & Architecture by Anirudha Puthraya.
"""

import sys
import os
import time
try:
    if sys.platform != "win32":
        import readline
except ImportError:
    pass
from .colors import green, yellow, cyan, bold, dim, red, magenta, blue
from .runner import print_haven_exception
import haven
import odcs


BANNER = f"""
{bold(cyan('╔═══════════════════════════════════════════════════════════════╗'))}
{bold(cyan('║                    HAVEN LANGUAGE v1.0.0                      ║'))}
{bold(cyan('║     Open Digital Continuity Standard (ODCS Edition)           ║'))}
{bold(cyan('║        Specification & Architecture by Anirudha Puthraya      ║'))}
{bold(cyan('╚═══════════════════════════════════════════════════════════════╝'))}
Type {bold(':help')} for interactive commands, {bold(':syntax')} for cheat sheet, or {bold(':quit')} to exit.
"""

HELP_TEXT = f"""
{bold(cyan('Haven REPL Interactive Commands:'))}
  {green(':help')}             Display this help guide
  {green(':syntax')}           Display complete Haven natural syntax cheat sheet
  {green(':model')} / {green(':layers')} Display the formal 4-Layer ODCS architecture stack
  {green(':tele')}             Probe real-time network environmental telemetry (RTT/Mode)
  {green(':crdt')}             Demonstrate multi-master conflict-free convergence
  {green(':mesh')}             Run 3-node P2P gossip mesh partition & recovery simulation
  {green(':ledger')}           View current blocks in the active continuity ledger
  {green(':audit')}            Cryptographically verify the ledger hash chain
  {green(':vars')}             Inspect active user variables in the current session
  {green(':bench')} <code>     Benchmark a Haven statement or expression
  {green(':info')}             Display Haven runtime architecture & specifications
  {green(':clear')}            Clear the terminal screen
  {green(':history')}          View session command history
  {green(':quit')} / {green(':exit')}     Exit the REPL session
"""

SYNTAX_CHEAT_SHEET = f"""
{bold(cyan('Haven Natural English & Pipeline Syntax Cheat Sheet:'))}

  {bold('1. Natural English Assignment:')}
     {yellow('set x to 42')}
     {yellow('let name be "Haven Developer"')}

  {bold('2. Guard Conditions & Inverted Flow:')}
     {yellow('unless x == 0: print("Non-zero:", x)')}
     {yellow('until counter == 0: counter = counter - 1')}

  {bold('3. Ergonomic Loops:')}
     {yellow('repeat 3 times: print("Continuous execution")')}
     {yellow('for each item in [10, 20, 30]: print(item * 2)')}

  {bold('4. High-Speed Pipelining (|>, into):')}
     {yellow('[1, 2, 3, 4] |> len')}
     {yellow('"hello" |> str.upper(_) |> print')}
     {yellow('data into ledger')}

  {bold('5. ODCS Durable Records & Checkpointing:')}
     {yellow('durable record Asset: id: str, value: float')}
     {yellow('checkpoint {"asset_id": "001"} as "genesis" into ledger')}
     {yellow('verify record with record.odcs_hash()')}
"""


def start_repl() -> None:
    """Starts the Haven interactive REPL."""
    print(BANNER)

    # Initialize execution environment
    repl_globals = {
        "__name__": "__main__",
        "__doc__": "Haven Interactive REPL Session",
        "haven": haven,
        "odcs": odcs,
    }

    # Preload all haven & odcs symbols into REPL namespace
    for mod in (haven, odcs):
        for attr in getattr(mod, "__all__", []):
            if hasattr(mod, attr):
                repl_globals[attr] = getattr(mod, attr)

    builtins_keys = set(repl_globals.keys())

    history = []
    buffer = []

    prompt_primary = f"{cyan('haven')} ❯ "
    prompt_secondary = f"{dim('....')} ❯ "

    while True:
        try:
            prompt = prompt_secondary if buffer else prompt_primary
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Haven REPL. Goodbye!")
            break

        stripped = line.strip()

        # Handle REPL meta-commands
        if not buffer and stripped.startswith(":"):
            parts = stripped.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in (":quit", ":exit", ":q"):
                print("Goodbye!")
                break
            elif cmd == ":help":
                print(HELP_TEXT)
                continue
            elif cmd == ":syntax":
                print(SYNTAX_CHEAT_SHEET)
                continue
            elif cmd in (":model", ":layers", ":architecture"):
                from .odcs_tools import _cmd_model
                _cmd_model()
                continue
            elif cmd in (":tele", ":telemetry"):
                from .odcs_tools import _cmd_tele
                _cmd_tele()
                continue
            elif cmd == ":crdt":
                from .odcs_tools import _cmd_crdt
                _cmd_crdt([])
                continue
            elif cmd in (":mesh", ":gossip"):
                from .odcs_tools import _cmd_mesh
                _cmd_mesh([])
                continue
            elif cmd == ":ledger":
                _print_ledger(repl_globals)
                continue
            elif cmd == ":audit":
                _audit_ledger(repl_globals)
                continue
            elif cmd in (":vars", ":env"):
                _print_vars(repl_globals, builtins_keys)
                continue
            elif cmd == ":bench":
                if not arg:
                    print(f"{yellow('Usage:')} :bench <expression or statement>")
                else:
                    _benchmark_code(arg, repl_globals)
                continue
            elif cmd == ":info":
                from .info import print_info
                print_info()
                continue
            elif cmd == ":clear":
                os.system("cls" if sys.platform == "win32" else "clear")
                continue
            elif cmd == ":history":
                for idx, h in enumerate(history, start=1):
                    print(f"  {idx:03d}: {h}")
                continue
            else:
                print(f"{red('Unknown REPL command:')} {cmd}. Type :help for commands.")
                continue

        buffer.append(line)
        code_block = "\n".join(buffer)

        # Check if more lines are needed (e.g. block ending in :)
        if line.endswith(":") or (line and line[0] in (" ", "\t")):
            continue

        history.append(code_block)
        buffer.clear()

        # Attempt to compile and evaluate
        try:
            # First try evaluating as an expression to auto-print results
            compiled = compile(code_block, "<haven-repl>", "eval")
            result = eval(compiled, repl_globals)
            if result is not None:
                print(f"{green('⇒')} {repr(result)}")
        except SyntaxError:
            # If not an expression, compile as statement block
            try:
                compiled = compile(code_block, "<haven-repl>", "exec")
                exec(compiled, repl_globals)
            except Exception as e:
                print_haven_exception(e, "<haven-repl>", code_block)
        except Exception as e:
            print_haven_exception(e, "<haven-repl>", code_block)


def _benchmark_code(code_str: str, repl_globals: dict) -> None:
    """Benchmarks a snippet in the REPL."""
    try:
        is_expr = True
        try:
            compiled = compile(code_str, "<bench>", "eval")
        except SyntaxError:
            compiled = compile(code_str, "<bench>", "exec")
            is_expr = False

        # Warmup
        if is_expr:
            eval(compiled, repl_globals)
        else:
            exec(compiled, repl_globals)

        iterations = 1000
        start = time.perf_counter()
        if is_expr:
            for _ in range(iterations):
                eval(compiled, repl_globals)
        else:
            for _ in range(iterations):
                exec(compiled, repl_globals)
        duration_s = time.perf_counter() - start

        avg_us = (duration_s / iterations) * 1_000_000.0
        print(f"{bold(cyan('Benchmark Result:'))} {green(f'{avg_us:.3f} µs')} per run ({iterations} iterations)")
    except Exception as e:
        print_haven_exception(e, "<bench>", code_str)


def _print_vars(repl_globals: dict, builtins_keys: set) -> None:
    """Prints variables currently defined in the session."""
    user_vars = {k: v for k, v in repl_globals.items() if k not in builtins_keys and not k.startswith("_")}
    if not user_vars:
        print(dim("No user variables defined in this REPL session."))
        return

    print(f"\n{bold(cyan('Active Haven Session Variables:'))}")
    for k, v in sorted(user_vars.items()):
        val_repr = repr(v)
        if len(val_repr) > 50:
            val_repr = val_repr[:47] + "..."
        type_name = type(v).__name__
        print(f"  {bold(cyan(k))} ({dim(type_name)}): {val_repr}")
    print()


def _print_ledger(repl_globals: dict) -> None:
    from odcs import get_default_ledger
    ledger = get_default_ledger()
    entries = ledger.entries

    print(f"\n{bold(cyan('Default Continuity Ledger:'))} {green(ledger.name)}")
    print(f"Total Blocks: {bold(str(len(entries)))} | Head Hash: {cyan(ledger.head_hash[:20])}...\n")

    for e in entries:
        alias_str = f" [alias: {green(e.alias)}]" if e.alias else ""
        print(f"  #{e.index:02d} {dim(e.timestamp[:19])} | Hash: {cyan(e.entry_hash[:16])}... | Prev: {dim(e.prev_hash[:16])}...{alias_str}")
    print()


def _audit_ledger(repl_globals: dict) -> None:
    from odcs import get_default_ledger
    ledger = get_default_ledger()
    valid = ledger.verify_chain()

    if valid:
        print(f"\n{bold(green('✔ Default Ledger Chain AUDIT PASSED:'))} {len(ledger.entries)} block(s) cryptographically verified.\n")
    else:
        print(f"\n{bold(red('✖ Default Ledger Chain AUDIT FAILED!'))}\n")
