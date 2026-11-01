"""
Haven Project & Package Manifest Manager (haven.toml)
Provides project initialization, dependency specification, and ODCS continuity settings.
Standard Specification & Architecture by Anirudha Puthraya.
"""

import sys
import os
import json
from .colors import green, yellow, red, cyan, bold, dim


DEFAULT_TOML = """# ==============================================================================
# Haven Language Project Manifest (haven.toml)
# Open Digital Continuity Standard (ODCS-1.0.0)
# ==============================================================================

[project]
name = "{name}"
version = "0.1.0"
authors = ["{author}"]
description = "{desc}"
entry = "src/main.hvn"
haven_version = ">=1.0.0"

[continuity]
# Layer 1: Local WAL & Merkle Durability
enabled = true
ledger_path = "data/ledger.json"
journal_wal = true
rfc8785_canonical = true

# Layer 2: Distributed Transport & CRDT Consensus
sync_mode = "MULTI_MASTER_CRDT"
heartbeat_interval_ms = 5000

# Layer 3: Environmental Telemetry & Edge Probing
gateway_url = "https://api.odcs.in"
telemetry_probe = true

# Layer 4: Application Zero Intent Loss (ZIL)
zero_intent_loss = true
instant_receipt_minting = true

[dependencies]
# List package requirements here
# continuity_crypto = "1.0.0"
"""


def init_manifest(project_name: str = None, author: str = "Anirudha Puthraya", desc: str = "Continuity-native Haven application") -> int:
    manifest_path = "haven.toml"
    if os.path.exists(manifest_path):
        print(f"{bold(yellow('Notice:'))} 'haven.toml' already exists in the current directory.")
        return 0

    if not project_name:
        project_name = os.path.basename(os.path.abspath("."))

    content = DEFAULT_TOML.format(name=project_name, author=author, desc=desc)
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n{bold(green('✔ Created Haven Project Manifest:'))} {bold('haven.toml')}")
    print(f"  • Project Name: {cyan(project_name)}")
    print(f"  • Author      : {author}")
    print(f"  • Standard    : ODCS-1.0.0 (Layers 1-4 Configured)\n")
    return 0


def view_manifest() -> int:
    manifest_path = "haven.toml"
    if not os.path.exists(manifest_path):
        print(f"{bold(yellow('No haven.toml found.'))} Run {bold('haven pkg init')} to create one.")
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        print(f"\n{bold(cyan('Current Project Manifest (haven.toml):'))}")
        print(f.read())
    return 0


def handle_pkg_command(args: list) -> int:
    if not args or args[0] in ("-h", "--help", "help"):
        print(f"""
{bold(cyan('Haven Project & Package Manager (haven pkg)'))}

{bold('Commands:')}
  {green('init')} [name]      Initialize a new haven.toml project manifest
  {green('show')}, {green('view')}     Display the current haven.toml configuration
""")
        return 0

    sub = args[0].lower()
    if sub == "init":
        p_name = args[1] if len(args) > 1 else None
        return init_manifest(p_name)
    elif sub in ("show", "view", "info"):
        return view_manifest()
    else:
        print(f"{bold(red('Error:'))} Unknown pkg command '{sub}'.", file=sys.stderr)
        return 1

