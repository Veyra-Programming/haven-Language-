"""
Haven Language Preprocessor & Star Language Ergonomics Engine
Architecture & Specification by Anirudha Puthraya.
Standard: ODCS-1.0.0 & OFCS-1.0.0
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import re


def preprocess_haven(source_code: str) -> str:
    """
    Transforms Star Language syntax and Haven natural extensions into standard Haven bytecode AST.
    Supported Star Ergonomics:
      - 'use <module>'               -> 'import <module>'
      - 'variable <name> = <val>'    -> 'set <name> to <val>'
      - 'constant <NAME> = <val>'    -> 'remember <NAME> as <val>'
      - 'end' (block terminator)     -> 'pass'
      - '() -> <expr>'               -> 'lambda: <expr>'
      - '(x, y) -> <expr>'           -> 'lambda x, y: <expr>'
    """
    lines = source_code.splitlines()
    processed_lines = []

    for line in lines:
        stripped = line.strip()

        # 1. Skip comments and empty lines
        if not stripped or stripped.startswith("#"):
            processed_lines.append(line)
            continue

        indent = line[:len(line) - len(line.lstrip())]

        # 2. 'end' statement -> 'pass'
        if stripped == "end":
            processed_lines.append(indent + "pass")
            continue

        # 3. 'use <module>' -> 'import <module>'
        m_use = re.match(r'^(\s*)use\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s*$', line)
        if m_use:
            processed_lines.append(f"{m_use.group(1)}import {m_use.group(2)}")
            continue

        # 4. 'variable <name> = <val>' -> '<name> = <val>' (or 'set <name> to <val>')
        m_var = re.match(r'^(\s*)variable\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
        if m_var:
            lead, name, val = m_var.groups()
            processed_lines.append(f"{lead}set {name} to {val}")
            continue

        # 5. 'constant <NAME> = <val>' -> 'remember <NAME> as <val>'
        m_const = re.match(r'^(\s*)constant\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
        if m_const:
            lead, name, val = m_const.groups()
            processed_lines.append(f"{lead}remember {name} as {val}")
            continue

        # 6. Star Arrow Lambdas: '() -> expr' -> 'lambda: expr' (never in def/function/define statements)
        curr_line = line
        if not re.search(r'^\s*(def|function|define)\b', curr_line):
            curr_line = re.sub(r'\(\)\s*->\s*', 'lambda: ', curr_line)
            curr_line = re.sub(r'\(([a-zA-Z_][a-zA-Z0-9_,\s]*)\)\s*->\s*', r'lambda \1: ', curr_line)

        processed_lines.append(curr_line)

    return "\n".join(processed_lines)
