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
{bold(magenta('╔═══════════════════════════════════════════════════════════════╗'))}
{bold(cyan('║             ANI++ / HAVEN OMNIENGINE v3.0 GA                  ║'))}
{bold(cyan('║     Quantum-Causality JIT & Digital Continuity Platform       ║'))}
{bold(yellow('║        Specification & Architecture by Anirudha Puthraya      ║'))}
{bold(magenta('╚═══════════════════════════════════════════════════════════════╝'))}
"""


def print_help() -> None:
    print(BANNER)
    print(f"""{bold('Usage:')}
  ani <command> [arguments...]
  haven <command> [arguments...]
  ani <script.ani|.hvn> [arguments...]

{bold('Core Commands:')}
  {green('run')} <file.ani|.hvn> [args...]   Execute an Ani++ or Haven program with arguments
  {green('eval')}, {green('-c')} <code>               Evaluate code strings with native OmniEngine runtime
  {green('build')} <file.ani|.hvn>          Compile source to tamper-proof bytecode (.hvc)
  {green('omni')}, {green('engine')}                 Inspect OmniEngine 4D DAG, Entangled Memory & Healer stats
  {green('timeline')}                       Visual representation of the 4D Chrono-Causality DAG
  {green('heal')}                           Inspect autonomous healing incidents and cryptographic receipts
  {green('new')} <name> [options]           Scaffold a new Ani++ / Haven project or ODCS App
  {green('pkg')} <init|show>                Manage project manifest (haven.toml)
  {green('test')} [path] [options]          Run Ani++ and Haven test suites with live reporting
  {green('check')} <file.ani|.hvn>          Static syntax and ODCS integrity verification
  {green('fmt')} <file.ani|.hvn>            Format and normalize source code
  {green('doctor')}                         Run toolchain diagnosis & edge network health check
  {green('api')} <subcommand>               Institutional Edge API Gateway CLI (https://api.odcs.in)
  {green('repl')}                           Launch interactive Ani++ / Haven REPL with live ledger tools
  {green('articles')} [list|read|open]      Read architectural essays & articles by Anirudha Puthraya
  {green('odcs')} <subcommand> [args...]    ODCS audit, replay, inspection, and verification tools
  {green('info')}                           Display Ani++ / Haven runtime, OmniEngine, and ODCS info
  {green('serve')} [--port 8000] [--dir .] Launch platform-independent dynamic PHP/Haven web server
  {green('idle')}                           Launch the Ani++ / Haven Graphical IDE / Shell
  {green('version')}, {green('-V')}, {green('--version')}    Print language version and dual-identity info

{bold('Options for `new`:')}
  {yellow('--template')}, {yellow('-t')}   Template: {bold('odcs-app')} (default), {bold('odcs-algorithm')}, {bold('ani-engine')}, {bold('basic')}
  {yellow('--author')}         Author name (default: Anirudha Puthraya)
  {yellow('--desc')}           Project description

{bold('Examples:')}
  ani run my_service.ani
  haven run my_script.hvn
  ani omni
  ani test tests/
  ani repl
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

    # If the first argument is a script file path (.hvn, .haven, .ani, .ani++)
    if first_arg.endswith((".hvn", ".haven", ".ani", ".ani++", ".py")) or (os.path.exists(first_arg) and not os.path.isdir(first_arg)):
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

    elif cmd in ("omni", "engine"):
        from haven.engine import _GLOBAL_OMNI_ENGINE
        info = _GLOBAL_OMNI_ENGINE.info()
        print(f"\n{bold(cyan('====================================================='))}")
        print(f"{bold(magenta('        ANI++ / HAVEN OMNIENGINE STATUS              '))}")
        print(f"{bold(cyan('====================================================='))}")
        print(f"  {bold('Engine Name:')}       {green(info['engine'])}")
        print(f"  {bold('Engine Version:')}    {yellow(info['version'])}")
        print(f"  {bold('Uptime:')}            {info['uptime_seconds']:.2f}s")
        print(f"  {bold('4D DAG Nodes:')}      {cyan(str(info['timeline_nodes']))}")
        print(f"  {bold('Active Branches:')}   {info['timeline_branches']}")
        print(f"  {bold('Healed Incidents:')}  {green(str(info['healed_events']))}")
        print(f"  {bold('Cognitive Nodes:')}   {magenta(str(info['cognitive_nodes']))}")
        print(bold(cyan('=====================================================')) + '\n')
        return 0

    elif cmd == "timeline":
        from haven.engine import _GLOBAL_OMNI_ENGINE
        nodes = _GLOBAL_OMNI_ENGINE.chrono.get_timeline_graph()
        print(f"\n{bold(cyan('====================================================='))}")
        print(f"{bold(magenta('       4D CHRONO-CAUSALITY TIMELINE DAG              '))}")
        print(f"{bold(cyan('====================================================='))}")
        for n in nodes:
            branch_str = f"[{magenta(n['branch'])}]"
            action_str = bold(yellow(n['action']))
            node_id_str = cyan(n['node_id'])
            parent_str = dim(f"<- {n['parent_id']}") if n['parent_id'] else dim("(GENESIS)")
            hash_str = dim(n['causality_hash'][:16] + "...")
            print(f"  • {node_id_str} {branch_str} {action_str} {parent_str} [{hash_str}]")
        print(bold(cyan('=====================================================')) + '\n')
        return 0

    elif cmd == "heal":
        from haven.engine import _GLOBAL_OMNI_ENGINE
        history = _GLOBAL_OMNI_ENGINE.healer.healing_history
        print(f"\n{bold(cyan('====================================================='))}")
        print(f"{bold(magenta('      AUTONOMOUS LIVING INTENT HEALING LOGS          '))}")
        print(f"{bold(cyan('====================================================='))}")
        if not history:
            print(f"  {green('No system panics or healing incidents recorded. All invariants nominal.')}")
        else:
            for r in history:
                d = r.to_dict()
                print(f"  • [{red(d['error_type'])}] in '{bold(d['operation'])}'")
                print(f"    Strategy: {green(d['strategy'])} | Sealed: {dim(d['seal_hash'][:20])}...")
                print(f"    Healed Result: {cyan(d['healed_value'])}")
        print(bold(cyan('=====================================================')) + '\n')
        return 0

    elif cmd == "idle":
        import idlelib.pyshell
        idlelib.pyshell.main()
        return 0

    elif cmd in ("serve", "server", "http"):
        parser = argparse.ArgumentParser(prog="haven serve", description="Launch platform-independent development web server")
        parser.add_argument("-p", "--port", type=int, default=8000, help="Port to listen on (default: 8000)")
        parser.add_argument("-H", "--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
        parser.add_argument("-d", "--dir", default=".", help="Document root directory (default: current directory)")
        ns = parser.parse_args(subargs)
        from haven.web import serve
        serve(port=ns.port, host=ns.host, document_root=ns.dir)
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

