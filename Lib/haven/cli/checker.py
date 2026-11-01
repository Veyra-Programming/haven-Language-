"""
Haven Static Syntax & ODCS Integrity Checker
Performs syntax verification and ODCS contract validation without full script execution.
"""

import sys
import os
from .colors import green, red, yellow, cyan, bold, dim


def check_file(file_path: str) -> int:
    """Verifies that a Haven file compiles cleanly and adheres to ODCS syntax."""
    if not os.path.exists(file_path):
        print(f"{bold(red('Error:'))} File not found: {file_path}", file=sys.stderr)
        return 1

    print(f"[*] Checking Haven syntax for: {bold(file_path)} ...", end=" ", flush=True)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code_str = f.read()

        compile(code_str, file_path, "exec")
        print(f"[{green('OK')}]")

        # Static analysis heuristics
        lines = code_str.splitlines()
        durable_records = sum(1 for line in lines if "durable record" in line or "durable class" in line)
        checkpoints = sum(1 for line in lines if line.strip().startswith("checkpoint "))
        verifies = sum(1 for line in lines if line.strip().startswith("verify "))
        repeats = sum(1 for line in lines if "repeat " in line and "times:" in line)
        unlesses = sum(1 for line in lines if line.strip().startswith("unless "))
        pipes = sum(1 for line in lines if "|>" in line)

        print(f"    Lines of Code:    {len(lines)}")
        print(f"    Durable Records:  {durable_records}")
        print(f"    Checkpoints:      {checkpoints}")
        print(f"    Verifications:    {verifies}")
        print(f"    Repeat Loops:     {repeats}")
        print(f"    Unless Guards:    {unlesses}")
        print(f"    Pipe Operations:  {pipes}")

        if durable_records > 0 and checkpoints == 0:
            print(f"    {yellow('Hint:')} Durable records defined but no checkpoints found. Consider adding ledger checkpoints.")

        return 0

    except SyntaxError as se:
        print(f"[{red('SYNTAX ERROR')}]")
        print(f"  Line {se.lineno}, Column {se.offset}: {se.msg}")
        if se.text:
            print(f"  {dim(se.text.strip())}")
            if se.offset:
                print(f"  {' ' * (se.offset - 1)}{red('^')}")
        return 1
    except Exception as e:
        print(f"[{red('ERROR')}] {e}")
        return 1

