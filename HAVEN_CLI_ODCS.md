# Haven Language CLI Tools & ODCS Continuity Framework
**Standard:** Open Digital Continuity Standard (ODCS-1.0.0)  
**Specification & Architecture Author:** Anirudha Puthraya  
**Language Runtime:** Haven Programming Language v1.0.0  

---

## 1. Unified Command Line Tools (`haven`)

Haven provides a developer CLI tool suite accessible via `haven`, `haven.bat`, `haven.cmd`, and `haven.ps1`.

### Core Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `haven run <script>` | Runs a Haven (`.hvn`, `.haven`) program | `haven run src/main.hvn --time` |
| `haven eval <code>` / `-c` | Directly evaluates Haven code strings | `haven -c "set x to 42; print(x)"` |
| `haven new <name>` | Scaffolds ODCS app systems & continuity algorithm packages | `haven new MyLedgerApp --template odcs-app` |
| `haven test [path]` | Automated test runner discovering & executing `.hvn` suites | `haven test tests/` |
| `haven check <file>` | Static syntax & ODCS integrity analysis without full execution | `haven check src/main.hvn` |
| `haven fmt <file>` | Code formatter & indentation normalizer for Haven files | `haven fmt src/main.hvn` |
| `haven repl` | Interactive Haven REPL with live ledger tools & syntax helpers | `haven repl` |
| `haven odcs <subcmd>`| Cryptographic audit, journal replay, proof verification | `haven odcs audit journal.json` |
| `haven info` | Displays compiler version, runtime substrate & ODCS spec info | `haven info` |
| `haven idle` | Launches the graphical Haven IDE / Shell | `haven idle` |

---

## 2. Project & Package Scaffolding (`haven new`)

### A. Scaffold an ODCS Application System (`--template odcs-app`)
Creates an ODCS-based application system with verifiable state transitions, durable records, and cryptographic ledger chaining:

```bash
haven new BankingLedger --template odcs-app --author "Anirudha Puthraya"
```

**Generated Architecture:**
- `haven.toml`: Application manifest and configuration
- `src/main.hvn`: Application entry point written in native Haven language
- `src/algorithm.hvn`: Custom ODCS Continuity Algorithm verifying invariants
- `src/models.hvn`: Sealed domain entities using `durable record`
- `src/service.hvn`: Application service wrapping `ODCSApp`
- `tests/test_app.hvn`: Test suite verifying immutability, transitions, and ledger
- `run.bat`: Single-click project launcher

### B. Scaffold an ODCS Continuity Algorithm Package (`--template odcs-algorithm`)
Creates a reusable ODCS Continuity Algorithm package:

```bash
haven new ConsensusEngine --template odcs-algorithm --author "Anirudha Puthraya"
```

**Generated Architecture:**
- `haven.toml`: Package manifest
- `src/algorithm.hvn`: Algorithm subclassing `ContinuityAlgorithm`
- `tests/test_algorithm.hvn`: Deterministic replay & invariant test suite

---

## 3. ODCS Cryptographic Continuity CLI (`haven odcs`)

The `haven odcs` toolkit provides auditing and disaster recovery tools:

```bash
# 1. Full Cryptographic Ledger Audit
haven odcs audit data/ledger_journal.json

# 2. Disaster Recovery Journal Replay
haven odcs replay data/ledger_journal.json

# 3. Block-Level Inspection
haven odcs inspect data/ledger_journal.json

# 4. Cryptographic Proof Verification
haven odcs verify <asset_or_file> <proof_hash>

# 5. Display ODCS Standards
haven odcs info
```

---

## 4. ODCS Continuity Algorithm Framework (`odcs.algorithm` / `haven.algorithm`)

### Available Continuity Algorithms

1. **`ContinuityAlgorithm` (Abstract Base Class)**: Contract governing transition validation, deterministic next-state evaluation, state hashing, and replay.
2. **`StateContinuityAlgorithm`**: Finite state machine with global invariant guards and action validators.
3. **`ConsensusContinuityAlgorithm`**: Quorum consensus engine verifying threshold multi-actor signatures.
4. **`EventSourcingContinuityAlgorithm`**: Append-only event stream engine with Merkle snapshotting and zero-loss state reconstruction.
5. **`ODCSApp`**: Production application system integrating continuity algorithms with append-only ledgers, durable records, audit report generation, journal export/replay, and embedded HTTP microservice API (`/api/status`, `/api/state`, `/api/dispatch`, `/api/audit`, `/api/ledger`).

