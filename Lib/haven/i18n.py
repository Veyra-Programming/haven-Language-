"""
Haven Universal Global Natural Dialects Engine (UGND)
Standard: Open Digital Continuity Standard (ODCS) Global Accessibility Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Empowers developers across every nation to write Haven in their native language
or dialect while maintaining 100% interoperable bytecode and cryptographic execution.
"""

import re
from typing import Dict, List, Tuple


# Global Dialect Translation Rules: (Regex Pattern, Replacement Pattern)
DIALECT_RULES: List[Tuple[re.Pattern, str]] = [
    # 1. Spanish (Español)
    (re.compile(r'^(\s*)establecer\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+a\s+(.+)$'), r'\1set \2 to \3'),
    (re.compile(r'^(\s*)repetir\s+(\d+|[a-zA-Z_][a-zA-Z0-9_]*)\s+veces\s*:\s*$'), r'\1repeat \2 times:'),
    (re.compile(r'^(\s*)devolver\s+(.+)$'), r'\1give back \2'),
    (re.compile(r'^(\s*)devolver\s*$'), r'\1give back'),
    (re.compile(r'^(\s*)mostrar\s+(.+)$'), r'\1show \2'),
    (re.compile(r'^(\s*)decir\s+(.+)$'), r'\1say \2'),
    (re.compile(r'^(\s*)siempre\s*:\s*$'), r'\1forever:'),
    (re.compile(r'^(\s*)mientras\s+(.+):\s*$'), r'\1while \2:'),

    # 2. Hindi / Hinglish (हिन्दी)
    (re.compile(r'^(\s*)rakho\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+barabar\s+(.+)$'), r'\1set \2 to \3'),
    (re.compile(r'^(\s*)dohrao\s+(\d+|[a-zA-Z_][a-zA-Z0-9_]*)\s+baar\s*:\s*$'), r'\1repeat \2 times:'),
    (re.compile(r'^(\s*)wapas_do\s+(.+)$'), r'\1give back \2'),
    (re.compile(r'^(\s*)wapas_do\s*$'), r'\1give back'),
    (re.compile(r'^(\s*)dikhao\s+(.+)$'), r'\1show \2'),
    (re.compile(r'^(\s*)hamesha\s*:\s*$'), r'\1forever:'),

    # 3. French (Français)
    (re.compile(r'^(\s*)definir\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+a\s+(.+)$'), r'\1set \2 to \3'),
    (re.compile(r'^(\s*)repeter\s+(\d+|[a-zA-Z_][a-zA-Z0-9_]*)\s+fois\s*:\s*$'), r'\1repeat \2 times:'),
    (re.compile(r'^(\s*)renvoyer\s+(.+)$'), r'\1give back \2'),
    (re.compile(r'^(\s*)renvoyer\s*$'), r'\1give back'),
    (re.compile(r'^(\s*)afficher\s+(.+)$'), r'\1show \2'),
    (re.compile(r'^(\s*)toujours\s*:\s*$'), r'\1forever:'),

    # 4. German (Deutsch)
    (re.compile(r'^(\s*)setze\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+auf\s+(.+)$'), r'\1set \2 to \3'),
    (re.compile(r'^(\s*)wiederhole\s+(\d+|[a-zA-Z_][a-zA-Z0-9_]*)\s+mal\s*:\s*$'), r'\1repeat \2 times:'),
    (re.compile(r'^(\s*)gib_zurueck\s+(.+)$'), r'\1give back \2'),
    (re.compile(r'^(\s*)gib_zurueck\s*$'), r'\1give back'),
    (re.compile(r'^(\s*)zeige\s+(.+)$'), r'\1show \2'),
    (re.compile(r'^(\s*)fuer_immer\s*:\s*$'), r'\1forever:'),

    # 5. Japanese (Romaji)
    (re.compile(r'^(\s*)settei\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+ni\s+(.+)$'), r'\1set \2 to \3'),
    (re.compile(r'^(\s*)kurikaeshi\s+(\d+|[a-zA-Z_][a-zA-Z0-9_]*)\s+kai\s*:\s*$'), r'\1repeat \2 times:'),
    (re.compile(r'^(\s*)kaesu\s+(.+)$'), r'\1give back \2'),
    (re.compile(r'^(\s*)kaesu\s*$'), r'\1give back'),
    (re.compile(r'^(\s*)hyouji\s+(.+)$'), r'\1show \2'),
]


def translate_dialects(source_code: str) -> str:
    """Translates global natural dialect lines into canonical Haven natural English."""
    lines = source_code.splitlines()
    output_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            output_lines.append(line)
            continue

        transformed = line
        for pattern, replacement in DIALECT_RULES:
            if pattern.search(transformed):
                transformed = pattern.sub(replacement, transformed)
                break
        output_lines.append(transformed)

    return "\n".join(output_lines)
