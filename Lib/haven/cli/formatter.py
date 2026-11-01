"""
Haven Code Formatter
Normalizes whitespace, indentation, and structure in Haven source code.
"""

import sys
import os
from .colors import green, red, yellow, cyan, bold, dim


def format_file(file_path: str, in_place: bool = True) -> int:
    """Formats a Haven source file."""
    if not os.path.exists(file_path):
        print(f"{bold(red('Error:'))} File not found: {file_path}", file=sys.stderr)
        return 1

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    formatted_lines = []

    for line in lines:
        stripped = line.rstrip()
        # Preserve blank lines
        if not stripped:
            formatted_lines.append("")
            continue
        
        # Normalize tab characters to 4 spaces
        tab_expanded = stripped.replace("\t", "    ")
        formatted_lines.append(tab_expanded)

    result = "\n".join(formatted_lines).strip() + "\n"

    if in_place:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"[{green('FORMATTED')}] {file_path}")
    else:
        sys.stdout.write(result)

    return 0

