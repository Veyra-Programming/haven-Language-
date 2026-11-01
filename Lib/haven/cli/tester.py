"""
Haven Test Runner
Discovers and executes Haven (.hvn, .haven) test suites with detailed reporting.
Standard Specification & Architecture by Anirudha Puthraya.
"""

import sys
import os
import time
import glob
from .colors import green, red, yellow, cyan, bold, dim
from .runner import run_script


def run_tests(target_path: str = ".", pattern: str = None, verbose: bool = False) -> int:
    """Discovers and runs test files in target directory or single test file."""
    test_files = []

    if os.path.isfile(target_path):
        test_files = [os.path.abspath(target_path)]
    elif os.path.isdir(target_path):
        search_pattern = pattern or "test_*.hvn"
        for root, dirs, files in os.walk(target_path):
            # Exclude build, cache, Lib internal tests, and git dirs
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "PCbuild", "dist", "externals", "Doc", "Misc", "Modules", "Objects", "Parser", "PC", "Programs", "Python") and not (target_path in (".", "./", ".\\") and d == "Lib")]
            for f in files:
                if (f.startswith("test_") or f.endswith("_test.hvn") or f.endswith("_test.py")) and (f.endswith(".hvn") or f.endswith(".py")):
                    test_files.append(os.path.abspath(os.path.join(root, f)))
    else:
        print(f"{bold(red('Error:'))} Path not found: '{target_path}'", file=sys.stderr)
        return 1

    if not test_files:
        print(f"{yellow('No test files found matching criteria in:')} {target_path}")
        return 0

    print(f"\n{bold(cyan('====================================================='))}")
    print(f"{bold(cyan('            Haven Language Test Suite Runner          '))}")
    print(f"{bold(cyan('====================================================='))}")
    print(f"[*] Found {len(test_files)} test suite(s). Starting execution...\n")

    passed_count = 0
    failed_count = 0
    start_total = time.perf_counter()

    for idx, test_file in enumerate(test_files, start=1):
        rel_path = os.path.relpath(test_file)
        print(f"[{idx}/{len(test_files)}] Running: {bold(rel_path)} ...", end=" ", flush=True)

        t0 = time.perf_counter()
        exit_code = run_script(test_file, script_args=[], measure_time=False, verbose=verbose)
        duration_ms = (time.perf_counter() - t0) * 1000.0

        if exit_code == 0:
            passed_count += 1
            print(f"[{green('PASS')}] ({duration_ms:.1f}ms)")
        else:
            failed_count += 1
            print(f"[{red('FAIL')}] ({duration_ms:.1f}ms)")

    total_time = (time.perf_counter() - start_total) * 1000.0

    print(f"\n{bold(cyan('====================================================='))}")
    print(f"{bold('Test Summary:')} {len(test_files)} total, {green(str(passed_count) + ' passed')}, {red(str(failed_count) + ' failed') if failed_count else '0 failed'}")
    print(f"{bold('Total Duration:')} {total_time:.2f} ms")
    print(f"{bold(cyan('====================================================='))}")

    return 0 if failed_count == 0 else 1
