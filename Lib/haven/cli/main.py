"""
Haven Command Line Interface (CLI)
Unified developer tooling for Haven Language & Open Digital Continuity Standard (ODCS).
Standard Specification & Architecture by Anirudha Puthraya.
"""

import sys
import os
import argparse
from .colors import green, yellow, cyan, bold, dim, red, blue, magenta
import haven
import odcs


BANNER = f"""
{bold(cyan('╔═══════════════════════════════════════════════════════════════╗'))}
{bold(cyan('║                    HAVEN LANGUAGE v1.0.0                      ║'))}
{bold(cyan('║     Open Digital Continuity Standard (ODCS Edition)           ║'))}
{bold(cyan('║        Specification & Architecture by Anirudha Puthraya      ║'))}
{bold(cyan('╚═══════════════════════════════════════════════════════════════╝'))}
"""


def print_help() -> None:
    print(BANNER)
    print(f"""{bold('Usage:')}
  haven <command> [arguments...]
  haven <script.hvn> [arguments...]

{bold('Core Commands:')}
  {green('run')} <file.hvn> [args...]       Execute a Haven program (.hvn, .haven) with arguments
  {green('eval')}, {green('-c')} <code>               Evaluate Haven code strings with native runtime
  {green('build')} <file.hvn>              Compile Haven source to tamper-proof bytecode (.hvc)
  {green('new')} <name> [options]           Scaffold a new ODCS App, Continuity Algorithm, or Haven project
  {green('pkg')} <init|show>                Manage project manifest (haven.toml)
  {green('test')} [path] [options]          Run Haven and ODCS test suites with live reporting
  {green('check')} <file.hvn>               Static syntax and ODCS integrity verification
  {green('fmt')} <file.hvn>                 Format and normalize Haven source code
  {green('doctor')}                         Run toolchain diagnosis & edge network health check
  {green('api')} <subcommand>               Institutional Edge API Gateway CLI (https://api.odcs.in)
  {green('repl')}                           Launch interactive Haven REPL with live ledger tools
  {green('articles')} [list|read|open]      Read architectural essays & articles by the Admin (Anirudha Puthraya)
  {green('odcs')} <subcommand> [args...]    ODCS audit, replay, inspection, and verification tools
  {green('info')}                           Display Haven runtime, ODCS spec, and environment info
  {green('idle')}                           Launch the Haven Graphical IDE / Shell
  {green('version')}, {green('-V')}, {green('--version')}    Print Haven language version information

{bold('Options for `haven new`:')}
  {yellow('--template')}, {yellow('-t')}   Template to use: {bold('odcs-app')} (default), {bold('odcs-algorithm')}, {bold('basic')}
  {yellow('--author')}         Author name (default: Anirudha Puthraya)
  {yellow('--desc')}           Project description

{bold('Examples:')}
  haven run my_script.hvn
  haven new MyBankingSystem --template odcs-app
  haven new ConsensusEngine --template odcs-algorithm
  haven test tests/
  haven check src/main.hvn
  haven odcs audit data/journal.json
  haven repl
""")


def main(args: list = None) -> int:
    if args is None:
        args = sys.argv[1:]

    # If no arguments provided:
    if not args:
        # Check if stdin is a tty -> launch REPL
        if sys.stdin.isatty():
            from .repl import start_repl
            start_repl()
            return 0
        else:
            print_help()
            return 0

    first_arg = args[0]

    # Quick flags
    if first_arg in ("-h", "--help", "help"):
        print_help()
        return 0

    if first_arg in ("-v", "-V", "--version", "version", "-version"):
        print(f"Haven {haven.__version__} [{haven.__standard__} by {haven.__author__}]")
        return 0

    if first_arg == "-c" or first_arg.lower() == "eval":
        code_args = args[1:]
        if not code_args:
            print(f"{bold(red('Error:'))} Code string required: haven -c <code>", file=sys.stderr)
            return 1
        from .runner import run_code
        return run_code(" ".join(code_args))

    # If the first argument is a script file path (.hvn, .haven)
    if first_arg.endswith((".hvn", ".haven", ".py")) or (os.path.exists(first_arg) and not os.path.isdir(first_arg)):
        from .runner import run_script
        return run_script(first_arg, args[1:])

    # Route Subcommands
    cmd = first_arg.lower()
    subargs = args[1:]

    if cmd == "run":
        if not subargs:
            print(f"{bold(red('Error:'))} Script path required: haven run <file.hvn>", file=sys.stderr)
            return 1
        
        # Check for --time or -t flag
        measure_time = False
        verbose = False
        remaining = []
        for a in subargs:
            if a in ("--time", "-t"):
                measure_time = True
            elif a in ("--verbose", "-V"):
                verbose = True
            else:
                remaining.append(a)

        if not remaining:
            print(f"{bold(red('Error:'))} Script path required: haven run <file.hvn>", file=sys.stderr)
            return 1

        from .runner import run_script
        return run_script(remaining[0], remaining[1:], measure_time=measure_time, verbose=verbose)

    elif cmd == "new":
        parser = argparse.ArgumentParser(prog="haven new", description="Scaffold a new Haven project or ODCS package")
        parser.add_argument("name", help="Name of the project or package")
        parser.add_argument("-t", "--template", default="odcs-app", help="Template: odcs-app, odcs-algorithm, basic")
        parser.add_argument("--author", default="Anirudha Puthraya", help="Author name")
        parser.add_argument("--desc", default="", help="Project description")
        parser.add_argument("-d", "--dir", default=".", help="Target directory")

        try:
            parsed = parser.parse_args(subargs)
        except SystemExit as se:
            return se.code

        from .scaffolder import scaffold_project
        return scaffold_project(
            name=parsed.name,
            template=parsed.template,
            author=parsed.author,
            description=parsed.desc,
            target_dir=parsed.dir
        )

    elif cmd == "test":
        parser = argparse.ArgumentParser(prog="haven test", description="Run Haven test suites")
        parser.add_argument("path", nargs="?", default=".", help="Directory or file path to run tests from")
        parser.add_argument("-p", "--pattern", default=None, help="Test file glob pattern")
        parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

        try:
            parsed = parser.parse_args(subargs)
        except SystemExit as se:
            return se.code

        from .tester import run_tests
        return run_tests(target_path=parsed.path, pattern=parsed.pattern, verbose=parsed.verbose)

    elif cmd == "check":
        if not subargs:
            print(f"{bold(red('Error:'))} File path required: haven check <file.hvn>", file=sys.stderr)
            return 1
        from .checker import check_file
        return check_file(subargs[0])

    elif cmd == "fmt":
        if not subargs:
            print(f"{bold(red('Error:'))} File path required: haven fmt <file.hvn>", file=sys.stderr)
            return 1
        from .formatter import format_file
        return format_file(subargs[0])

    elif cmd == "repl":
        from .repl import start_repl
        start_repl()
        return 0

    elif cmd in ("articles", "article", "essays", "essay", "read"):
        from .articles import handle_articles_command
        return handle_articles_command(subargs)

    elif cmd == "odcs":
        from .odcs_tools import handle_odcs_command
        return handle_odcs_command(subargs)

    elif cmd in ("info", "sysinfo", "diagnostics"):
        from .info import print_info
        return print_info()

    elif cmd in ("doctor", "diag", "health"):
        from .doctor import run_doctor
        return run_doctor()

    elif cmd == "api":
        from .api_cli import handle_api_command
        return handle_api_command(subargs)

    elif cmd == "build":
        if not subargs:
            print(f"{bold(red('Error:'))} Source file path required: haven build <file.hvn>", file=sys.stderr)
            return 1
        from .builder import build_file
        out_p = subargs[1] if len(subargs) > 1 else None
        return build_file(subargs[0], out_p)

    elif cmd in ("pkg", "package", "manifest"):
        from .pkg import handle_pkg_command
        return handle_pkg_command(subargs)

    elif cmd == "idle":
        import idlelib.pyshell
        idlelib.pyshell.main()
        return 0

    else:
        # Check if first_arg could be a script with omitted extension
        candidate = None
        for ext in (".hvn", ".haven", ".py"):
            if os.path.exists(first_arg + ext):
                candidate = first_arg + ext
                break
        if candidate:
            from .runner import run_script
            return run_script(candidate, subargs)

        print(f"{bold(red('Error:'))} Unknown command '{first_arg}'. Type {bold('haven --help')} for available commands.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

