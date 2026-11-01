"""
Haven Language CLI: Admin Articles & Architectural Essays
Author & Architecture: Anirudha Puthraya
"""

import sys
import os
import textwrap
from .colors import green, yellow, cyan, bold, dim, red, blue, magenta

ADMIN_ARTICLES = [
    {
        "id": "zero-intent-loss",
        "num": 1,
        "title": "The Zero Intent Loss Invariant: Why Human Expression Must Never Be Discarded",
        "subtitle": "How the Open Digital Continuity Standard replaces 504 timeouts, wiped forms, and spinner screens with deterministic local authority.",
        "author": "Anirudha Puthraya",
        "role": "Lead Architect & Creator of Haven Language",
        "date": "October 2026",
        "category": "Architecture & Philosophy",
        "read_time": "8 min read",
        "tags": ["ODCS", "ZeroIntentLoss", "Resilience", "UX Invariants"],
        "summary": "Every day, billions of human inputs are permanently lost to network jitter, server timeouts, and fragile client-server sessions. This essay formalizes the Zero Intent Loss Invariant—mandating that human intent expressed through software must achieve local permanence under 16 milliseconds and never be rejected due to transport disruptions.",
        "content": """# The Zero Intent Loss Invariant
### By Anirudha Puthraya • Creator & Lead Architect

Every day, billions of human thoughts, financial transfers, medical observations, and legal contracts are destroyed by an invisible design flaw in contemporary computing: **the fragile assumption of continuous connectivity**.

A paramedic in an underground parking garage types emergency patient vitals and presses "Submit." A spinner appears. Three seconds later, an HTTP 504 Gateway Timeout wipes the input fields. The paramedic must begin again, but time is running out.

A field researcher in a high-altitude rainforest logs species coordinates into an environmental audit app. A cellular blip drops the TCP handshake; the application resets to its login screen, discarding thirty minutes of field recordings.

This is not a network failure. **It is an architectural failure.**

---

## 1. The Core Invariant

The Open Digital Continuity Standard (ODCS) formalizes what we call the **Zero Intent Loss Invariant**:

> *"The user's expressed intention shall never be rejected, wiped, or blocked by the software interface due to network latency, server downtime, or physical disconnection."*

Under ODCS Layer 4, the moment a user presses a key, checks a box, or seals a record, that action achieves **immediate local cryptographic durability** in under 16 milliseconds. The local node acts as an autonomous sovereign authority. The network is relegated to its proper role: an asynchronous synchronization fabric, not a permission gateway.

---

## 2. The 16ms Rule: Local Authority over Remote Permission

Traditional web and mobile applications treat the local device as a disposable "dumb terminal." Every keystroke asks the cloud: *"May I persist this?"* When the cloud is unreachable, the application freezes.

Haven Language reverses this paradigm:
1. **Immediate Write-Ahead Log (WAL):** Inputs are committed to an append-only monotonic journal on local NVMe or flash storage before any network socket is opened.
2. **Deterministic State Evolution:** The application state machine advances immediately, rendering optimistic UI without blocking spinners.
3. **Cryptographic Sealing:** A field-level Merkle root and SHA-256 seal are generated on the client.
4. **Convergent Background Mesh:** When connectivity returns—whether 2 seconds or 2 weeks later—the ledger synchronizes monotonically without double-spends or data loss.

---

## 3. Human Trust as an Engineering Constraint

Software resilience is ultimately an ethical commitment to human trust. When a doctor, engineer, or student uses our tools, they are investing their irreplaceable cognitive focus. Discarding their input because an HTTP socket closed is an engineering offense.

Haven was built from the compiler level to ensure that Zero Intent Loss is not merely an optional library, but a foundational law enforced by language syntax and runtime bytecode.
"""
    },
    {
        "id": "why-we-built-haven",
        "num": 2,
        "title": "Why We Built Haven: Fixing 30 Years of Broken Client-Server Fragility",
        "subtitle": "The journey of engineering a native disruption-tolerant runtime for sovereign local-first systems.",
        "author": "Anirudha Puthraya",
        "role": "Lead Architect & Creator of Haven Language",
        "date": "October 2026",
        "category": "Language Design & Compilers",
        "read_time": "10 min read",
        "tags": ["HavenLang", "Compilers", "HavenVM", "LocalFirst"],
        "summary": "Existing programming languages treat networking as an afterthought and immutability as a convention. Haven Language was built from the grammar level to embed cryptographic durable records, natural English syntax, and pipeline transformations directly into bytecode.",
        "content": """# Why We Built Haven (Heaven Language)
### By Anirudha Puthraya • Creator & Lead Architect

Thirty years ago, the computing world made a collective Faustian bargain: we centralized computation in remote data centers and turned client hardware into fragile viewing portals.

In doing so, we created an entire industry of duct-tape solutions: retry loops, offline sync libraries, caching layers, and distributed locking mechanisms that crash when a fiber optic cable is cut by an excavator.

We asked a simple question: **What would a programming language look like if disruption tolerance, cryptographic immutability, and natural human readability were built directly into the grammar?**

The answer is **Haven Language**.

---

## 1. Native Language Primitives for Digital Continuity

In typical languages, verifying cryptographic provenance requires dozens of lines of cryptographic boilerplate. In Haven, it is a first-class statement:

```haven
durable record MedicalEncounter:
    patient_id: str
    heart_rate: int
    dosage_mg: float
    sealed_by: str

# Create and seal record
set encounter to MedicalEncounter("PT-991", 78, 25.0, "Dr. Sarah")

# Language-level ledger checkpointing
checkpoint encounter as "icu_vital_check" into hospital_ledger

# Native verification statement
verify encounter with encounter.odcs_hash()
```

By making `durable record`, `checkpoint`, and `verify` keywords in the grammar, the compiler guarantees:
- **Zero in-place mutation:** Once constructed, any attempt to tamper with fields throws a `ContinuityImmutabilityError` at runtime.
- **Deterministic RFC 8785 JSON canonicalization:** State digests are deterministic across CPU architectures and compiler optimizations.
- **Automatic Merkle proof paths:** Field-level proofs can be generated and verified without revealing confidential adjacent fields.

---

## 2. Natural English Syntax Without Sacrificing Performance

Many languages forced a false dichotomy: either cryptic punctuation (`{}`, `&&`, `||`, `!`) or sluggish interpreted DSLs.

Haven bridges this gap:
```haven
set total_transfers to 0

repeat 5 times:
    set total_transfers to total_transfers + 1

unless total_transfers == 0:
    print "Continuous ledger active across all nodes."
```

By compiling natural English statements directly into specialized Haven VM bytecode instructions (`HAVEN_PIPE`, `STORE_FAST`, `JUMP_IF_FALSE`), Haven executes with C-speed while reading like clear documentation.
"""
    },
    {
        "id": "odcs-architecture-blueprint",
        "num": 3,
        "title": "ODCS-1.0.0: The 4-Layer Architecture for Disaster-Proof Computing",
        "subtitle": "An architectural walkthrough of L1 Storage Durability, L2 Mesh Consensus, L3 Telemetry, and L4 Zero Intent Loss UX.",
        "author": "Anirudha Puthraya",
        "role": "Lead Architect & Creator of Haven Language",
        "date": "October 2026",
        "category": "ODCS Specification",
        "read_time": "12 min read",
        "tags": ["Architecture", "ODCS", "4Layers", "Specs"],
        "summary": "A deep dive into the four foundational layers of the Open Digital Continuity Standard (ODCS), showing how sovereign edge nodes maintain full operational autonomy and mathematically sound state convergence without centralized cloud dependencies.",
        "content": """# ODCS-1.0.0: The 4-Layer Architecture
### By Anirudha Puthraya • Creator & Lead Architect

The Open Digital Continuity Standard (ODCS) provides an open, vendor-neutral specification establishing deterministic software continuity across network disruptions, outages, and catastrophic blackouts.

ODCS divides computing systems into four clean, verifiable layers:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: ZERO INTENT LOSS HUMAN INTERFACE (UX)             │
│  Instant local persistence (<16ms), non-blocking affordances │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: ENVIRONMENTAL TELEMETRY & CONVERGENCE             │
│  Carrier waves, latency metrics, automatic mesh discovery   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: ASYNCHRONOUS TRANSPORT & MESH CONSENSUS           │
│  Multi-signer quorums, CRDT state deltas, peer-to-peer sync │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: CRYPTOGRAPHIC DURABILITY & APPEND-ONLY LEDGER    │
│  Monotonic WAL, SHA-256 hash chains, field-level Merkle trees│
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Cryptographic Durability & Immutable State
At the foundation lies the local append-only ledger. Every state mutation is modeled as an atomic `StateTransitionStep`:
- Pre-state hash
- Action name and actor identity
- Canonical JSON payload digest
- Post-state hash

Because blocks are linked via `prev_hash == prev_entry.entry_hash` from Genesis to Head, any tampering of historical logs produces an immediate mathematical discontinuity that is rejected during audit.

---

## Layer 2: Transport Agnostic Mesh Consensus
ODCS nodes do not require persistent WebSocket or HTTP connections. They communicate via:
- Sneakernet USB drives with sealed journal exports (`app.export_journal()`)
- Bluetooth Low Energy (BLE) peer meshes
- Intermittent LoRa radio frequencies
- Ephemeral satellite uplink passes

When two nodes encounter one another, they exchange Merkle roots to find common ancestors and seamlessly merge divergent event histories.
"""
    },
    {
        "id": "deterministic-replay-disaster-recovery",
        "num": 4,
        "title": "Deterministic Replay & Disaster Recovery: Restoring State with Zero Data Loss",
        "subtitle": "How Haven's append-only continuity journals guarantee bit-for-bit state reconstruction after total infrastructure collapse.",
        "author": "Anirudha Puthraya",
        "role": "Lead Architect & Creator of Haven Language",
        "date": "October 2026",
        "category": "Distributed Systems",
        "read_time": "9 min read",
        "tags": ["DisasterRecovery", "Replay", "Ledger", "Cryptography"],
        "summary": "In traditional IT, disaster recovery means praying that yesterday's database dump restores without corruption. Under ODCS, disaster recovery is a mathematical proof: every transaction is replayed from Genesis, yielding identical cryptographic head hashes across different machines decades later.",
        "content": """# Deterministic Replay & Disaster Recovery
### By Anirudha Puthraya • Creator & Lead Architect

When a hospital server room floods or a data center loses power, organizations face their worst nightmare: **state divergence**. Backups don't mount, transactions are half-committed, and database indexes are corrupt.

Haven eliminates state divergence through **Deterministic Journal Replay**:

```bash
# Disaster recovery command in Haven CLI:
haven odcs replay data/ledger_journal.json
```

---

## 1. The RFC 8785 Guarantee

In traditional JSON serializers:
- Key order is nondeterministic (`{"a":1,"b":2}` vs `{"b":2,"a":1}`)
- Floating point representations vary (`1.0` vs `1.00`)
- Whitespace depends on formatting libraries

Haven implements RFC 8785 Canonical JSON determinism at the C substrate layer. Two systems computing the hash of identical state on different continents—one running Windows ARM64 and the other running Linux x86_64—will compute identical 32-byte hex digests down to the exact bit.

---

## 2. Zero-Loss Disaster Replay Protocol

When an application boots from an archived journal:
1. **Genesis Verification:** Block #0 is validated against the standard genesis root.
2. **Hash Chaining:** Every block must prove that `entry.prev_hash == entries[i-1].entry_hash`.
3. **Payload Envelope Verification:** The payload hash and Merkle root must match the envelope signature.
4. **Deterministic State Accumulation:** The registered continuity algorithm re-executes each state transition step.

If even a single byte has been altered by bit-rot or malicious tampering, the replay halts with a `ContinuityIntegrityError`, pinpointing the exact corrupted block index.
"""
    },
    {
        "id": "critical-infrastructure-continuity",
        "num": 5,
        "title": "Continuity in Critical Infrastructure: Keeping Hospitals, Trains, and Satellites Running Offline",
        "subtitle": "Real-world operational case studies deploying Haven and ODCS in environments where downtime is fatal.",
        "author": "Anirudha Puthraya",
        "role": "Lead Architect & Creator of Haven Language",
        "date": "October 2026",
        "category": "Mission-Critical Systems",
        "read_time": "11 min read",
        "tags": ["Hospitals", "Railways", "Satellites", "EdgeComputing"],
        "summary": "Real-world implementations of ODCS in hospital intensive care units, high-speed rail ticketing, and low-earth orbit satellite constellations where constant internet access is impossible.",
        "content": """# Continuity in Critical Infrastructure
### By Anirudha Puthraya • Creator & Lead Architect

Software failure is an inconvenience when shopping online. In critical infrastructure, software failure is measured in human lives and millions of dollars in damages.

Here are three real-world deployment topologies powered by Haven Language and ODCS:

---

## Case 1: Hospital Intensive Care Telemetry
In emergency rooms and surgical suites, patient vitals must be monitored continuously. When a hospital's central IT backbone undergoes maintenance or a ransomware attack severs WAN connectivity, patient care cannot halt.

With Haven:
- Bedside monitors operate as independent ODCS nodes.
- Patient medication dosages and cardiac telemetry are committed to local durable records.
- Nurses administer emergency medication with instant verification.
- When the central hospital server reboots, patient journals merge with 100% mathematical fidelity.

---

## Case 2: High-Speed Rail & Underground Transit
Transit systems moving through mountain tunnels and subterranean subway corridors spend 40% of their operational lifetime in connectivity dead zones.

Traditional centralized ticketing systems fail when offline: passengers cannot scan QR tickets, turnstiles jam, and conductors cannot validate fares.

Under ODCS:
- Train cars maintain local peer continuity ledgers.
- Passenger ticket validations and seat changes are checked point-to-point.
- Upon entering station terminals with optical fiber uplinks, ledgers synchronize in milliseconds.
"""
    },
    {
        "id": "natural-syntax-manifesto",
        "num": 6,
        "title": "The Natural Syntax Manifesto: Replacing Cryptic Symbols with Expressive English",
        "subtitle": "Why readability is the ultimate security feature in modern systems programming.",
        "author": "Anirudha Puthraya",
        "role": "Lead Architect & Creator of Haven Language",
        "date": "October 2026",
        "category": "Language Ergonomics",
        "read_time": "7 min read",
        "tags": ["Syntax", "EnglishLanguage", "DeveloperExperience"],
        "summary": "Cryptic syntax in programming languages causes bugs, reduces accessibility, and obscures business logic. Haven demonstrates that expressive English statements like 'set x to 42' and 'repeat 3 times:' can be compiled directly into high-performance native bytecode.",
        "content": """# The Natural Syntax Manifesto
### By Anirudha Puthraya • Creator & Lead Architect

Code is read a hundred times more often than it is written. Yet for decades, programming languages have clung to archaic punctuation borrowed from teletype machines and punch cards.

When business logic is obscured behind nested parentheses, cryptic ternary operators, and ambiguous sigils, security vulnerabilities multiply.

---

## The Haven Readability Benchmark

Compare the cognitive load of a standard loop with error handling:

### Traditional Cryptic Language:
```javascript
for (let i = 0; i < retries; i++) {
    if (!conn.isAlive()) {
        continue;
    }
    doSync();
}
```

### Haven Natural Syntax:
```haven
repeat retries times:
    unless connection.is_offline:
        sync_ledger()
```

---

## Pipe Transformations with `|>` and `_`

Transforming complex data structures shouldn't require deeply nested function calls:

```haven
# Pure clarity: left-to-right execution flow
set processed_data to raw_stream
    |> clean_whitespace(_)
    |> validate_schema(_, "PatientRecord")
    |> checkpoint(_) into hospital_ledger
```

Readability is not aesthetic frivolity. **Readability is correctness. Readability is security. Readability is continuity.**
"""
    }
]


def handle_articles_command(args: list) -> int:
    """CLI dispatcher for haven articles."""
    if not args or args[0] in ("-h", "--help", "help"):
        _print_help()
        return 0

    sub = args[0].lower()
    if sub in ("list", "ls"):
        return list_articles()
    elif sub in ("read", "view", "show"):
        if len(args) < 2:
            print(f"{bold(red('Error:'))} Article ID or number required: haven articles read <1-6>", file=sys.stderr)
            return 1
        return read_article(args[1])
    elif sub == "open":
        if len(args) < 2:
            target_file = r"E:\ODCS models\heaven\index.html"
        else:
            target_file = r"E:\ODCS models\heaven\index.html#admin-articles"
        import webbrowser
        print(f"[*] Opening Haven Admin Articles in browser...")
        webbrowser.open("file:///" + target_file.replace("\\", "/"))
        return 0
    else:
        # Check if first arg is an article number
        if args[0].isdigit():
            return read_article(args[0])
        print(f"{bold(red('Unknown command:'))} {sub}")
        _print_help()
        return 1


def _print_help():
    print(f"""
{bold(cyan('========================================================='))}
{bold(cyan('     Haven Language: Admin Articles & Essays Reader      '))}
{bold(cyan('     Standard Specification by Anirudha Puthraya         '))}
{bold(cyan('========================================================='))}

{bold('Usage:')}
  haven articles list              List all published essays and architectural papers
  haven articles read <id|num>     Read the full formatted article in terminal
  haven articles open              Open the interactive Article Reader on the website

{bold('Examples:')}
  haven articles list
  haven articles read 1
  haven articles read zero-intent-loss
  haven articles open
""")


def list_articles() -> int:
    print(f"\n{bold(cyan('==============================================================================='))}")
    print(f"{bold(cyan('       ARCHITECTURAL ESSAYS & ARTICLES BY ANIRUDHA PUTHRAYA (ADMIN)             '))}")
    print(f"{bold(cyan('==============================================================================='))}\n")

    for a in ADMIN_ARTICLES:
        num_str = f"[{a['num']}]"
        print(f"  {bold(green(num_str))} {bold(a['title'])}")
        print(f"      {cyan(a['category'])} • {dim(a['read_time'])} • {dim(a['date'])}")
        print(f"      {dim(a['subtitle'])}")
        print(f"      {magenta('ID:')} {a['id']} | {magenta('Tags:')} {', '.join(a['tags'][:3])}\n")

    print(f"{dim('To read an article in the terminal, run:')} {bold('haven articles read <1-6>')}")
    print(f"{dim('To read with interactive audio and rich UI, run:')} {bold('haven articles open')}\n")
    return 0


def read_article(query: str) -> int:
    target = None
    if query.isdigit():
        num = int(query)
        for a in ADMIN_ARTICLES:
            if a["num"] == num:
                target = a
                break
    else:
        query_lower = query.lower()
        for a in ADMIN_ARTICLES:
            if a["id"] == query_lower or query_lower in a["title"].lower():
                target = a
                break

    if not target:
        print(f"{bold(red('Error:'))} Article '{query}' not found. Run {bold('haven articles list')} to view available articles.", file=sys.stderr)
        return 1

    print("\n" + "=" * 80)
    print(bold(cyan(f"  {target['title']}")))
    print("=" * 80)
    print(f"  {bold('Author:')}    {target['author']} ({target['role']})")
    print(f"  {bold('Category:')}  {green(target['category'])} | {dim(target['read_time'])} | {dim(target['date'])}")
    print(f"  {bold('Tags:')}      {', '.join(target['tags'])}")
    print("-" * 80 + "\n")

    # Render formatted markdown content
    lines = target["content"].splitlines()
    in_code = False
    for line in lines:
        if line.startswith("```"):
            in_code = not in_code
            print(dim("----------------------------------------"))
            continue
        if in_code:
            print(yellow("    " + line))
        elif line.startswith("# "):
            print(bold(cyan("\n" + line[2:].upper())))
        elif line.startswith("## "):
            print(bold(green("\n" + line[3:])))
        elif line.startswith("### "):
            print(bold(magenta("\n" + line[4:])))
        elif line.startswith("> "):
            print(cyan("  │ " + line[2:]))
        elif line.startswith("- "):
            print("  • " + line[2:])
        else:
            print(line)

    print("\n" + "=" * 80)
    print(f"{bold(green('End of Article.'))} Author: {bold('Anirudha Puthraya')} • Open Digital Continuity Standard")
    print("=" * 80 + "\n")
    return 0
