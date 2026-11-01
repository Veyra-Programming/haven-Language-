"""
Haven Script & Code Runner
Executes Haven (.hvn, .haven) programs and code strings with environment configuration,
argument forwarding, and high-precision timing.
Standard Specification & Architecture by Anirudha Puthraya.
"""

import sys
import os
import time
import linecache
from .colors import green, red, yellow, cyan, bold, dim, magenta
import haven
import odcs


def print_haven_exception(e: Exception, file_path: str = None, code_str: str = None) -> None:
    """Formats and prints an unhandled exception with beautiful Haven diagnostics."""
    from haven import ContinuityImmutabilityError
    from odcs import ContinuityIntegrityError

    print(f"\n{bold(red('╔═══════════════════════════════════════════════════════════════╗'))}", file=sys.stderr)
    print(f"{bold(red('║                     HAVEN EXECUTION ERROR                     ║'))}", file=sys.stderr)
    print(f"{bold(red('╚═══════════════════════════════════════════════════════════════╝'))}", file=sys.stderr)

    if isinstance(e, (ContinuityImmutabilityError, ContinuityIntegrityError)):
        print(f"{bold(yellow('[ODCS SECURITY VIOLATION]'))} {bold(str(e))}", file=sys.stderr)
        print(dim("The Open Digital Continuity Standard (ODCS) strictly prohibited illegal mutation or hash tampering."), file=sys.stderr)
        return

    exc_type = type(e).__name__
    print(f"  {bold('Exception:')}  {bold(red(exc_type))}: {e}", file=sys.stderr)

    # If it's a SyntaxError, show the exact line and position
    if isinstance(e, SyntaxError):
        loc_file = e.filename or file_path or "<haven-input>"
        loc_line = e.lineno or 1
        loc_col = e.offset or 1
        print(f"  {bold('Location:')}   {loc_file} [Line {loc_line}, Col {loc_col}]", file=sys.stderr)
        if e.text:
            text = e.text.rstrip()
            print(f"\n  {dim(f'{loc_line:4d} |')} {text}", file=sys.stderr)
            pad = " " * (len(f"{loc_line:4d} | ") + loc_col - 1)
            print(f"  {pad}{bold(red('^'))}", file=sys.stderr)
    else:
        # Format traceback frames cleanly
        tb = e.__traceback__
        frames = []
        while tb:
            frame = tb.tb_frame
            lineno = tb.tb_lineno
            co = frame.f_code
            filename = co.co_filename
            funcname = co.co_name
            # Skip internal runner frames
            if not filename.endswith("runner.py"):
                frames.append((filename, lineno, funcname))
            tb = tb.tb_next

        if frames:
            print(f"  {bold('Call Trace (most recent call last):')}", file=sys.stderr)
            for f_name, f_line, f_fn in frames:
                fn_str = f" in {cyan(f_fn)}" if f_fn != "<module>" else ""
                print(f"    • {dim(f_name)}:{bold(str(f_line))}{fn_str}", file=sys.stderr)
                source_line = linecache.getline(f_name, f_line).strip()
                if source_line:
                    print(f"        {dim(source_line)}", file=sys.stderr)


def run_code(code_str: str) -> int:
    """Executes a Haven code string directly."""
    import types

    main_mod = types.ModuleType("__main__")
    main_mod.__file__ = "<haven-string>"
    main_globals = main_mod.__dict__
    main_globals["haven"] = haven
    main_globals["odcs"] = odcs

    # Inject Haven & ODCS symbols
    for mod in (haven, odcs):
        for attr in getattr(mod, "__all__", []):
            if hasattr(mod, attr):
                main_globals[attr] = getattr(mod, attr)

    sys.modules["__main__"] = main_mod

    try:
        compiled = compile(code_str, "<haven-eval>", "exec")
        exec(compiled, main_globals)
        return 0
    except SystemExit as se:
        return se.code if isinstance(se.code, int) else (0 if se.code is None else 1)
    except Exception as e:
        print_haven_exception(e, "<haven-eval>", code_str)
        return 1


def run_script(file_path: str, script_args: list, measure_time: bool = False, verbose: bool = False) -> int:
    """Executes a Haven script file and returns exit code."""
    if not os.path.exists(file_path):
        # Try checking with extensions (.hvn, .haven, .hvc)
        found = None
        for ext in (".hvn", ".haven", ".hvc", ".py"):
            candidate = file_path + ext
            if os.path.exists(candidate):
                found = candidate
                break
        if found:
            file_path = found
        else:
            print(f"{bold(red('Error:'))} File not found: '{file_path}'", file=sys.stderr)
            return 1

    old_argv = list(sys.argv)
    old_sys_path = list(sys.path)
    old_modules = set(sys.modules.keys())
    old_main = sys.modules.get("__main__")

    file_path = os.path.abspath(file_path)
    script_dir = os.path.dirname(file_path)

    # Ensure script's directory and package root are in sys.path
    for p in (script_dir, os.path.dirname(script_dir), os.getcwd()):
        if p and p not in sys.path:
            sys.path.insert(0, p)

    # Prepare sys.argv for the target script
    sys.argv = [file_path] + script_args

    if verbose:
        print(dim(f"[*] Executing Haven script: {file_path}"))
        print(dim(f"[*] Arguments: {script_args}"))

    start_time = time.perf_counter()
    exit_code = 0

    import types
    main_mod = types.ModuleType("__main__")
    main_mod.__file__ = file_path
    main_globals = main_mod.__dict__
    main_globals["haven"] = haven
    main_globals["odcs"] = odcs

    # Inject Haven builtins
    for mod in (haven, odcs):
        for attr in getattr(mod, "__all__", []):
            if hasattr(mod, attr):
                main_globals[attr] = getattr(mod, attr)

    sys.modules["__main__"] = main_mod

    try:
        if file_path.endswith(".hvc"):
            import marshal
            with open(file_path, "rb") as f:
                header = f.read(8)
                compiled = marshal.load(f)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                code_str = f.read()
            compiled = compile(code_str, file_path, "exec")

        exec(compiled, main_globals)

    except SystemExit as se:
        exit_code = se.code if isinstance(se.code, int) else (0 if se.code is None else 1)
    except Exception as e:
        exit_code = 1
        print_haven_exception(e, file_path)
    finally:
        sys.argv = old_argv
        sys.path = old_sys_path
        if old_main is not None:
            sys.modules["__main__"] = old_main
        # Remove newly imported modules to avoid cross-project caching collisions
        for m in list(sys.modules.keys()):
            if m not in old_modules:
                sys.modules.pop(m, None)

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    if measure_time:
        print(dim(f"\n[Execution completed in {duration_ms:.2f} ms with exit code {exit_code}]"))

    return exit_code
