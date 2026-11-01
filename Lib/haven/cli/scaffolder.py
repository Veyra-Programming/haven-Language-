"""
Haven Project & Package Scaffolder
Creates new ODCS-based App Systems, Continuity Algorithm packages, and standard Haven applications.
"""

import os
import sys
from .colors import green, yellow, cyan, bold, dim


def scaffold_project(
    name: str,
    template: str = "odcs-app",
    author: str = "Anirudha Puthraya",
    description: str = "",
    target_dir: str = "."
) -> int:
    """Scaffolds a new project directory with chosen template."""
    project_path = os.path.abspath(os.path.join(target_dir, name))
    
    if os.path.exists(project_path) and os.listdir(project_path):
        print(f"{bold(yellow('Warning:'))} Directory '{project_path}' already exists and is not empty.", file=sys.stderr)
        return 1

    os.makedirs(project_path, exist_ok=True)

    template = template.lower().strip()
    if template in ("odcs-app", "app", "odcs"):
        return _scaffold_odcs_app(project_path, name, author, description)
    elif template in ("odcs-algorithm", "algorithm", "algo"):
        return _scaffold_odcs_algorithm(project_path, name, author, description)
    elif template in ("basic", "standard", "starter"):
        return _scaffold_basic_project(project_path, name, author, description)
    else:
        print(f"{bold(yellow('Error:'))} Unknown template '{template}'. Available templates: odcs-app, odcs-algorithm, basic", file=sys.stderr)
        return 1


def _write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")


def _scaffold_odcs_app(path: str, name: str, author: str, desc: str) -> int:
    """Scaffolds a complete production ODCS-based Application System."""
    desc = desc or f"Production ODCS-based Application System with verifiable cryptographic continuity."

    # 1. haven.toml
    haven_toml = f"""[project]
name = "{name}"
version = "1.0.0"
author = "{author}"
description = "{desc}"
standard = "ODCS-1.0.0"
specification_author = "Anirudha Puthraya"
entrypoint = "src/main.hvn"

[app]
type = "odcs-app"
algorithm = "{name}ContinuityAlgorithm"
auto_checkpoint = true
ledger_name = "{name}-Primary-Ledger"

[dependencies]
haven = ">=1.0.0"
odcs = ">=1.0.0"
"""
    _write_file(os.path.join(path, "haven.toml"), haven_toml)

    # 2. README.md
    readme = f"""# {name} - ODCS Application System
**Standard:** Open Digital Continuity Standard (ODCS-1.0.0)  
**Architecture & Specification:** Anirudha Puthraya  
**Author:** {author}  

{desc}

---

## Architecture Overview

This application is built on the **Haven Programming Language** and implements the **Open Digital Continuity Standard (ODCS)**:
- **Durable Records:** Field-level immutability post-initialization preventing state tampering.
- **Continuity Algorithm:** Verifiable finite state machine guaranteeing pre- and post-condition invariants.
- **Append-Only Cryptographic Ledger:** SHA-256 hash chaining from Genesis to Head block.
- **Zero-Loss Disaster Recovery:** Replay journal export & cryptographic integrity verification.
- **Embedded Verifiable Microservice:** Embedded HTTP server exposing `/api/state`, `/api/dispatch`, `/api/audit`, `/api/ledger`.

---

## Directory Structure

```
{name}/
├── haven.toml             # ODCS application manifest and configuration
├── README.md              # Project documentation and specifications
├── run.bat                # Single-click launcher
├── src/
│   ├── main.hvn           # Main entry point and demo lifecycle
│   ├── algorithm.hvn      # Custom ODCS Continuity Algorithm
│   ├── models.hvn         # Domain durable records
│   └── service.hvn        # Application state management service
└── tests/
    └── test_app.hvn       # Verifiable test suite (immutability, transitions, ledger)
```

---

## How to Run

### 1. Run the Application
```bash
haven run src/main.hvn
```
or click `run.bat`.

### 2. Run the Test Suite
```bash
haven test tests/
```

### 3. Cryptographic Ledger Audit
```bash
haven odcs audit data/journal.json
```
"""
    _write_file(os.path.join(path, "README.md"), readme)

    # 3. src/models.hvn
    models_hvn = """# Domain Models with ODCS Durable Immutability
# Standard Specification & Architecture by Anirudha Puthraya

from odcs import durable_record, ContinuityImmutabilityError

# 1. Sealed Asset Entity
durable record AssetRecord:
    def __init__(self, asset_id, owner, asset_type, balance, status):
        self.asset_id = asset_id
        self.owner = owner
        self.asset_type = asset_type
        self.balance = balance
        self.status = status

# 2. Sealed Transaction Receipt
durable record AuditReceipt:
    def __init__(self, receipt_id, action, actor, timestamp, prev_hash, post_hash):
        self.receipt_id = receipt_id
        self.action = action
        self.actor = actor
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.post_hash = post_hash
"""
    _write_file(os.path.join(path, "src", "models.hvn"), models_hvn)

    # 4. src/algorithm.hvn
    algorithm_hvn = f"""# Custom ODCS Continuity Algorithm for {name}
# Standard Specification & Architecture by Anirudha Puthraya

from odcs import StateContinuityAlgorithm, ContinuityIntegrityError

to create_app_algorithm():
    set algo to StateContinuityAlgorithm(
        algorithm_id="{name}ContinuityAlgorithm",
        version="1.0.0",
        description="Continuity algorithm guaranteeing balance non-negativity and authorized ownership transfers."
    )

    # Invariant: total registered assets must never have negative balance
    def invariant_no_negative_balance(state):
        set assets to state.get("assets", {{}})
        for asset_id, item in assets.items():
            if item.get("balance", 0) < 0:
                return False
        return True

    algo.add_invariant(invariant_no_negative_balance)

    # Action 1: REGISTER_ASSET
    def handle_register(current_state, payload, actor):
        set next_state to dict(current_state)
        set assets to dict(next_state.get("assets", {{}}))
        set asset_id to payload["asset_id"]

        assets[asset_id] = {{
            "asset_id": asset_id,
            "owner": payload.get("owner", actor),
            "asset_type": payload.get("asset_type", "digital_token"),
            "balance": float(payload.get("balance", 0.0)),
            "created_by": actor
        }}
        next_state["assets"] = assets
        return next_state

    def validate_register(current_state, payload, actor):
        set asset_id to payload.get("asset_id")
        unless asset_id:
            return False
        set assets to current_state.get("assets", {{}})
        if asset_id in assets:
            return False  # Duplicate asset ID prevented
        if float(payload.get("balance", 0.0)) < 0.0:
            return False
        return True

    algo.register_transition("REGISTER_ASSET", handle_register, validate_register)

    # Action 2: TRANSFER_BALANCE
    def handle_transfer(current_state, payload, actor):
        set next_state to dict(current_state)
        set assets to dict(next_state.get("assets", {{}}))

        set from_id to payload["from_asset_id"]
        set to_id to payload["to_asset_id"]
        set amount to float(payload["amount"])

        set sender to dict(assets[from_id])
        set receiver to dict(assets[to_id])

        sender["balance"] = sender["balance"] - amount
        receiver["balance"] = receiver["balance"] + amount

        assets[from_id] = sender
        assets[to_id] = receiver
        next_state["assets"] = assets
        return next_state

    def validate_transfer(current_state, payload, actor):
        set from_id to payload.get("from_asset_id")
        set to_id to payload.get("to_asset_id")
        set amount to float(payload.get("amount", 0.0))

        if amount <= 0.0:
            return False

        set assets to current_state.get("assets", {{}})
        if from_id not in assets or to_id not in assets:
            return False

        set sender_balance to assets[from_id].get("balance", 0.0)
        if sender_balance < amount:
            return False  # Insufficient funds

        return True

    algo.register_transition("TRANSFER_BALANCE", handle_transfer, validate_transfer)
    return algo
"""
    _write_file(os.path.join(path, "src", "algorithm.hvn"), algorithm_hvn)

    # 5. src/service.hvn
    service_hvn = f"""# ODCS Application System Service
# Standard Specification & Architecture by Anirudha Puthraya

from odcs import ODCSApp
from src.algorithm import create_app_algorithm

to create_app():
    set algo to create_app_algorithm()
    set initial_state to {{
        "app_title": "{name}",
        "assets": {{}},
        "version": "1.0.0"
    }}

    set app to ODCSApp(
        name="{name}",
        algorithm=algo,
        initial_state=initial_state,
        author="{author}"
    )
    return app
"""
    _write_file(os.path.join(path, "src", "service.hvn"), service_hvn)

    # 6. src/main.hvn
    main_hvn = f"""# {name} - Main Entry Point
# Open Digital Continuity Standard (ODCS) Implementation
# Standard Specification & Architecture by Anirudha Puthraya

import os
from src.models import AssetRecord
from src.service import create_app

to main():
    print("================================================================")
    print("  🚀 Initializing ODCS App: {name}")
    print("  Open Digital Continuity Standard (ODCS) by Anirudha Puthraya")
    print("================================================================")

    # Initialize ODCS App Engine
    set app to create_app()
    print("[*] ODCS App initialized with Cryptographic Ledger.")
    print(f"[*] Genesis Head Hash: {{app.ledger.head_hash}}")

    # Step 1: Register initial asset records
    print("\\n--- [1] Dispatching State Transitions ---")
    set entry1 to app.dispatch(
        action="REGISTER_ASSET",
        payload={{"asset_id": "VAULT-A", "owner": "Alice", "balance": 10000.0}},
        actor="Alice"
    )
    print(f"[+] Asset 'VAULT-A' Registered! Ledger Block #{{entry1.index}} Sealed: {{entry1.entry_hash[:20]}}...")

    set entry2 to app.dispatch(
        action="REGISTER_ASSET",
        payload={{"asset_id": "VAULT-B", "owner": "Bob", "balance": 2500.0}},
        actor="Bob"
    )
    print(f"[+] Asset 'VAULT-B' Registered! Ledger Block #{{entry2.index}} Sealed: {{entry2.entry_hash[:20]}}...")

    # Step 2: Verifiable State Transfer
    print("\\n--- [2] Executing Verifiable Balance Transfer ---")
    set entry3 to app.dispatch(
        action="TRANSFER_BALANCE",
        payload={{"from_asset_id": "VAULT-A", "to_asset_id": "VAULT-B", "amount": 3500.0}},
        actor="Alice"
    )
    print(f"[+] Transfer 3500.0 from VAULT-A to VAULT-B Succeeded!")
    print(f"[+] Ledger Block #{{entry3.index}} Hash: {{entry3.entry_hash[:20]}}...")

    # Step 3: Verify App State & Merkle Root
    print("\\n--- [3] Current Application State & Cryptographic Proofs ---")
    set curr_state to app.get_state()
    print("State Assets:", curr_state["assets"])
    print("State Hash:  ", app.get_state_hash())
    print("Merkle Root: ", app.get_merkle_root())

    # Step 4: Full Cryptographic Continuity Audit
    print("\\n--- [4] Performing Full Cryptographic Ledger Audit ---")
    set audit_report to app.audit()
    print(f"[*] Status:                  {{audit_report['status']}}")
    print(f"[*] Chain Integrity Valid:   {{audit_report['chain_integrity_valid']}}")
    print(f"[*] Total Blocks:            {{audit_report['total_ledger_blocks']}}")
    print(f"[*] Head Hash:               {{audit_report['head_hash']}}")

    # Step 5: Export Journal for Long-Term Digital Continuity & Disaster Recovery
    os.makedirs("data", exist_ok=True)
    set journal_file to "data/ledger_journal.json"
    app.export_journal(journal_file)
    print(f"\\n[+] Sealed continuity journal exported to: {{journal_file}}")

    print("\\n================================================================")
    print("  ✓ {name} ODCS EXECUTION & CONTINUITY COMPLETED!")
    print("================================================================")

if __name__ == "__main__":
    main()
"""
    _write_file(os.path.join(path, "src", "main.hvn"), main_hvn)

    # 7. tests/test_app.hvn
    test_hvn = f"""# Test Suite for {name} ODCS Application System
# Standard Specification & Architecture by Anirudha Puthraya

from odcs import ContinuityIntegrityError, ContinuityImmutabilityError
from src.models import AssetRecord
from src.service import create_app

to test_durable_record_immutability():
    set asset to AssetRecord("AST-01", "Charlie", "Token", 500.0, "ACTIVE")
    assert asset.asset_id == "AST-01"
    assert asset.balance == 500.0

    # Ensure field mutation is prevented
    set mutation_blocked to False
    try:
        asset.balance = 999999.0
    except ContinuityImmutabilityError:
        set mutation_blocked to True
    assert mutation_blocked is True
    print("[PASS] Durable Record Immutability Verified.")

to test_app_transitions_and_ledger():
    set app to create_app()
    set e1 to app.dispatch("REGISTER_ASSET", {{"asset_id": "ACC-1", "balance": 1000.0}}, actor="Admin")
    set e2 to app.dispatch("REGISTER_ASSET", {{"asset_id": "ACC-2", "balance": 500.0}}, actor="Admin")

    # Valid transfer
    set e3 to app.dispatch("TRANSFER_BALANCE", {{"from_asset_id": "ACC-1", "to_asset_id": "ACC-2", "amount": 400.0}})
    set state to app.get_state()
    assert state["assets"]["ACC-1"]["balance"] == 600.0
    assert state["assets"]["ACC-2"]["balance"] == 900.0

    # Invalid transfer: exceeds balance -> should fail
    set failed_overflow to False
    try:
        app.dispatch("TRANSFER_BALANCE", {{"from_asset_id": "ACC-1", "to_asset_id": "ACC-2", "amount": 10000.0}})
    except ContinuityIntegrityError:
        set failed_overflow to True
    assert failed_overflow is True

    # Audit validation
    set audit_res to app.audit()
    assert audit_res["chain_integrity_valid"] is True
    print("[PASS] State Transitions and Ledger Chain Integrity Verified.")

if __name__ == "__main__":
    print("Running {name} ODCS Verification...")
    test_durable_record_immutability()
    test_app_transitions_and_ledger()
    print("ALL TESTS PASSED!")
"""
    _write_file(os.path.join(path, "tests", "test_app.hvn"), test_hvn)

    # 8. run.bat
    run_bat = f"""@echo off
rem Launcher for {name} ODCS Application System
haven run src\\main.hvn %*
"""
    _write_file(os.path.join(path, "run.bat"), run_bat)

    print(f"\n{bold(green('✔ Successfully created ODCS Application System:'))} {bold(name)}")
    print(f"{dim('Directory:')} {path}")
    print(f"{dim('Template:')}  odcs-app (ODCS-1.0.0 by Anirudha Puthraya)")
    print(f"\n{bold('Next steps:')}")
    print(f"  cd {name}")
    print(f"  haven run src/main.hvn")
    print(f"  haven test tests/")
    return 0


def _scaffold_odcs_algorithm(path: str, name: str, author: str, desc: str) -> int:
    """Scaffolds a dedicated ODCS Continuity Algorithm Package."""
    desc = desc or f"Custom ODCS Continuity Algorithm package with cryptographic state verification."

    # 1. haven.toml
    haven_toml = f"""[project]
name = "{name}"
version = "1.0.0"
author = "{author}"
description = "{desc}"
standard = "ODCS-1.0.0"
specification_author = "Anirudha Puthraya"
type = "odcs-algorithm"

[algorithm]
name = "{name}"
class_name = "{name.capitalize()}Algorithm"
version = "1.0.0"

[dependencies]
haven = ">=1.0.0"
odcs = ">=1.0.0"
"""
    _write_file(os.path.join(path, "haven.toml"), haven_toml)

    # 2. README.md
    readme = f"""# {name} - ODCS Continuity Algorithm Package
**Standard:** Open Digital Continuity Standard (ODCS-1.0.0)  
**Architecture & Specification:** Anirudha Puthraya  
**Author:** {author}  

{desc}

---

## Features
- Implements `ContinuityAlgorithm` with deterministic transition validation
- Zero-knowledge Merkle state aggregation
- Invariant checking and tamper resistance
- Deterministic replay verification suite

---

## Usage

```haven
from {name} import {name.capitalize()}Algorithm

set algo to {name.capitalize()}Algorithm()
set next_state, step to algo.execute_step(current_state, "MY_ACTION", payload)
```
"""
    _write_file(os.path.join(path, "README.md"), readme)

    # 3. src/algorithm.hvn
    algo_hvn = f"""# {name.capitalize()}Algorithm - ODCS Continuity Algorithm Implementation
# Standard Specification & Architecture by Anirudha Puthraya

from odcs import ContinuityAlgorithm, ContinuityIntegrityError, MerkleTree

class {name.capitalize()}Algorithm(ContinuityAlgorithm):
    def __init__(self):
        super().__init__(
            algorithm_id="{name}",
            version="1.0.0",
            description="{desc}"
        )

    def validate_transition(self, current_state, action, payload, actor="system"):
        unless action:
            return False
        # Custom invariant verification logic
        return True

    def apply_transition(self, current_state, action, payload, actor="system"):
        set next_state to dict(current_state)
        set events to list(next_state.get("events", []))
        events.append({{"action": action, "actor": actor, "payload": payload}})
        next_state["events"] = events
        next_state["last_action"] = action
        return next_state
"""
    _write_file(os.path.join(path, "src", "algorithm.hvn"), algo_hvn)

    # 4. src/__init__.py
    init_py = f"""from src.algorithm import {name.capitalize()}Algorithm
__all__ = ["{name.capitalize()}Algorithm"]
"""
    _write_file(os.path.join(path, "src", "__init__.py"), init_py)

    # 5. tests/test_algorithm.hvn
    test_algo = f"""# Test Suite for {name.capitalize()}Algorithm
from src.algorithm import {name.capitalize()}Algorithm

to test_algorithm_transitions():
    set algo to {name.capitalize()}Algorithm()
    set initial_state to {{"events": [], "status": "INIT"}}

    set state1, step1 to algo.execute_step(initial_state, "START_SESSION", {{"session_id": "S1"}}, actor="Alice")
    assert state1["last_action"] == "START_SESSION"
    assert len(state1["events"]) == 1
    assert step1.post_state_hash is not None

    # Test replay determinism
    set replay_result to algo.replay_transitions(initial_state, [
        {{"action": "START_SESSION", "payload": {{"session_id": "S1"}}, "actor": "Alice", "post_state_hash": step1.post_state_hash}}
    ])
    assert replay_result["last_action"] == "START_SESSION"
    print("[PASS] Algorithm Transitions & Deterministic Replay Verified.")

if __name__ == "__main__":
    test_algorithm_transitions()
    print("ALL TESTS PASSED!")
"""
    _write_file(os.path.join(path, "tests", "test_algorithm.hvn"), test_algo)

    print(f"\n{bold(green('✔ Successfully created ODCS Continuity Algorithm Package:'))} {bold(name)}")
    print(f"{dim('Directory:')} {path}")
    print(f"{dim('Template:')}  odcs-algorithm (ODCS-1.0.0 by Anirudha Puthraya)")
    return 0


def _scaffold_basic_project(path: str, name: str, author: str, desc: str) -> int:
    """Scaffolds a basic starter Haven project."""
    haven_toml = f"""[project]
name = "{name}"
version = "0.1.0"
author = "{author}"
description = "{desc or 'A Haven Language application'}"
entrypoint = "src/main.hvn"
"""
    _write_file(os.path.join(path, "haven.toml"), haven_toml)

    main_hvn = f"""# {name} - Main Entry Point
to main():
    print("Hello from Haven Language!")
    set x to 10
    repeat 3 times:
        print("Haven count:", x)
        set x to x + 1

if __name__ == "__main__":
    main()
"""
    _write_file(os.path.join(path, "src", "main.hvn"), main_hvn)

    print(f"\n{bold(green('✔ Successfully created Haven Project:'))} {bold(name)}")
    return 0

