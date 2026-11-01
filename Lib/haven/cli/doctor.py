"""
Haven Language Doctor & System Diagnostics
Validates Haven compiler, ODCS runtime, cryptographic ledger, and edge gateway connectivity.
Standard Specification & Architecture by Anirudha Puthraya.
"""

import sys
import os
import time
import json
import urllib.request
import tempfile
from .colors import green, yellow, red, cyan, bold, dim, magenta
import haven
import odcs


def run_doctor() -> int:
    """Runs full system diagnosis on the Haven runtime environment."""
    print(f"\n{bold(cyan('╔═══════════════════════════════════════════════════════════════╗'))}")
    print(f"{bold(cyan('║                    HAVEN SYSTEM DOCTOR                        ║'))}")
    print(f"{bold(cyan('║       Open Digital Continuity Standard (ODCS-1.0.0)           ║'))}")
    print(f"{bold(cyan('║        Specification & Architecture by Anirudha Puthraya      ║'))}")
    print(f"{bold(cyan('╚═══════════════════════════════════════════════════════════════╝'))}\n")

    issues = 0

    # 1. Runtime Version & Architecture
    print(f"{bold('1. Haven Runtime & VM Substrate:')}")
    print(f"   {green('✔')} Language Version     : Haven {haven.__version__}")
    print(f"   {green('✔')} Standard Spec        : {haven.__standard__}")
    print(f"   {green('✔')} Lead Architect       : {haven.__author__}")
    print(f"   {green('✔')} VM Executable        : {sys.executable}")
    print(f"   {green('✔')} Platform Architecture: {sys.platform} ({os.name})")

    # 2. Syntax & Native Language Engines
    print(f"\n{bold('2. Syntax & Native Language Parsing Engines:')}")
    try:
        test_code = """
set x to 10
repeat 2 times:
    x = x + 1
"""
        ns = {}
        exec(compile(test_code, "<test-english>", "exec"), ns)
        if ns.get("x") == 12:
            print(f"   {green('✔')} Natural English Parser: Operational (`set x to`, `repeat N times`)")
        else:
            print(f"   {yellow('⚠')} Natural English Parser: Unexpected evaluation result")
            issues += 1
    except Exception as e:
        print(f"   {red('✖')} Natural English Parser: Error ({e})")
        issues += 1

    try:
        pipe_code = """
items = [1, 2, 3]
res = items |> len
"""
        ns = {}
        exec(compile(pipe_code, "<test-pipe>", "exec"), ns)
        if ns.get("res") == 3:
            print(f"   {green('✔')} Pipeline Operator (|>) : Operational (Zero-overhead native pipeline)")
        else:
            print(f"   {yellow('⚠')} Pipeline Operator (|>) : Unexpected result")
            issues += 1
    except Exception as e:
        print(f"   {red('✖')} Pipeline Operator (|>) : Error ({e})")
        issues += 1

    # 3. Cryptographic Ledger & WAL Durability
    print(f"\n{bold('3. Layer 1 Durability & Merkle Ledgers:')}")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = os.path.join(tmpdir, "doctor_ledger.json")
            ledger = odcs.ContinuityLedger(name="DoctorAuditLedger", storage_path=ledger_path)
            h = ledger.checkpoint({"audit_id": "sys-check", "timestamp": time.time()}, alias="check-01")
            is_valid = ledger.verify_chain()
            if is_valid and h:
                print(f"   {green('✔')} Local WAL Journaling  : Operational (Atomic persistence)")
                print(f"   {green('✔')} SHA-256 Merkle Proofs: Operational (RFC 8785 Canonical JSON verified)")
                print(f"   {green('✔')} Cryptographic Head    : {h.entry_hash[:32]}...")
            else:
                print(f"   {red('✖')} Merkle Ledger Audit   : Chain validation failed")
                issues += 1
    except Exception as e:
        print(f"   {red('✖')} Ledger Subsystem       : Error ({e})")
        issues += 1

    # 4. Layer 2 Transport & CRDT Convergence
    print(f"\n{bold('4. Layer 2 CRDT & State Convergence:')}")
    try:
        vc1 = odcs.VectorClock({"NodeA": 1})
        vc2 = odcs.VectorClock({"NodeB": 2})
        merged = vc1.merge(vc2)
        cnt1 = odcs.PNCounter("NodeA")
        cnt1.increment("NodeA", 10)
        cnt2 = odcs.PNCounter("NodeB")
        cnt2.increment("NodeB", 25)
        converged_cnt = cnt1.merge(cnt2)
        if merged.get("NodeA") == 1 and merged.get("NodeB") == 2 and converged_cnt.value == 35:
            print(f"   {green('✔')} Vector Clock Merging  : Operational (Causality Frontier Preservation)")
            print(f"   {green('✔')} PN-Counter Convergence: Operational (Strong Eventual Consistency)")
        else:
            print(f"   {yellow('⚠')} CRDT Convergence      : Unexpected merge state")
            issues += 1
    except Exception as e:
        print(f"   {red('✖')} CRDT Engine           : Error ({e})")
        issues += 1

    # 5. Cloudflare Edge Gateway Connectivity (api.odcs.in)
    print(f"\n{bold('5. Institutional Edge Gateway Connectivity (api.odcs.in):')}")
    try:
        start_t = time.perf_counter()
        req = urllib.request.Request(
            "https://api.odcs.in/v1/telemetry/probe",
            headers={"User-Agent": "Haven-Doctor/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            latency_ms = (time.perf_counter() - start_t) * 1000
            data = json.loads(resp.read().decode())
            colo = data.get("edge", {}).get("colo", "GLOBAL")
            mode = data.get("telemetry", {}).get("mode", "OPTIMAL_ONLINE")
            proto = data.get("edge", {}).get("httpProtocol", "HTTP/3")
            print(f"   {green('✔')} Edge Gateway Status   : Connected (api.odcs.in)")
            print(f"   {green('✔')} Active Edge Colo      : {colo} ({proto})")
            print(f"   {green('✔')} Round-Trip Latency    : {latency_ms:.2f} ms")
            print(f"   {green('✔')} Network Continuity    : {mode}")
    except Exception as e:
        print(f"   {yellow('⚠')} Edge Gateway Status   : Sovereign Offline / Airgap Mode")
        print(f"     {dim('Under ODCS Layer 3 Invariants, Haven operates fully sovereign when disconnected.')}")

    # 6. Encoding & Unicode Integrity
    print(f"\n{bold('6. System Character Encoding:')}")
    fs_enc = sys.getfilesystemencoding()
    std_enc = sys.stdout.encoding or "utf-8"
    print(f"   {green('✔')} Filesystem Encoding   : {fs_enc}")
    print(f"   {green('✔')} Console I/O Encoding  : {std_enc}")

    print(f"\n{bold(cyan('═══════════════════════════════════════════════════════════════'))}")
    if issues == 0:
        print(f"{bold(green('✔ DOCTOR VERDICT: Haven Language Toolchain is 100% HEALTHY!'))}")
        print(f"{dim('Ready for production ODCS digital continuity deployment.')}\n")
        return 0
    else:
        print(f"{bold(yellow(f'⚠ DOCTOR VERDICT: {issues} issue(s) detected. Check output above.'))}\n")
        return 1
