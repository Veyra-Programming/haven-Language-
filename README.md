# Haven Programming Language (Heaven Language)
### Standard: Open Digital Continuity Standard (ODCS-1.0.0)
**Specification & Architecture Author:** Anirudha Puthraya  
**Version:** 1.0.0 (Production Release)  
**Core Runtime:** Haven High-Performance Virtual Machine & ODCS Substrate  

---

## 🌟 Overview

**Haven** (also known as *Heaven Language*) is a modern, disruption-tolerant programming language engineered from the ground up for sovereign, local-first computing systems. 

Unlike traditional programming languages that treat network persistence and immutability as external libraries, Haven integrates **cryptographic continuity, durable memory records, natural English syntax, and pipeline transformations directly into the language grammar and runtime virtual machine**.

```haven
# 1. Natural English Assignment
set balance to 1000.00
let currency be "USD"

# 2. Hardware-Sealed Durable Records
durable record PaymentTransaction:
    tx_id: str
    sender: str
    receiver: str
    amount: float

# 3. Instantiate & Seal (Tamper-Proof)
set tx to PaymentTransaction("TX-9901", "Alice", "Bob", 250.00)

# 4. First-Class Continuity Checkpoint
checkpoint tx as "alice_payment" into global_treasury

# 5. Native Pipeline Chaining
set summary to [10, 20, 30] 
    |> map(lambda x: x * 2, _) 
    |> list 
    |> len

# 6. Guard Conditions
unless balance < 250.00:
    print f"Transaction verified! Ledger blocks: {len(global_treasury.entries)}"
```

---

## 🏛️ The Five Pillars of Haven Language

### 1. 🗣️ Natural English Syntax
Haven eliminates cryptic punctuation without sacrificing speed or precision:
- **Assignment:** `set x to 42`, `let rate be 0.05`
- **Conditionals:** `unless condition: ... else: ...`
- **Ergonomic Loops:** `repeat 5 times: ...`, `until done: ...`, `for each item in items: ...`
- **Function Declarations:** `to calculate(x, y): ...`, `function process(data): ...`

### 2. ⚡ First-Class Pipelining (`|>` and `into`)
Chain transformations cleanly from left to right with automatic or placeholder (`_`) argument binding:
```haven
set clean_tokens to raw_text
    |> str.strip
    |> str.lower
    |> str.split
```
Or send records directly into persistent ledgers:
```haven
transaction into treasury_ledger
```

### 3. 🛡️ Hardware-Backed Durable Records (`durable record`)
Records declared with `durable record` are sealed upon creation:
- **Zero in-place mutation:** Any attempt to alter fields raises `ContinuityImmutabilityError`.
- **Deterministic Canonicalization:** Hashes adhere strictly to RFC 8785 JSON canonicalization.
- **Genesis Cryptographic Hashes:** Automatically computed upon instantiation.

### 4. ⛓️ Cryptographic Continuity Ledgers & ODCS
Built-in cryptographic continuity ensuring mathematical verification:
- `checkpoint record as "alias" into ledger`
- `verify asset with expected_proof`
- Append-only Merkle DAG validation
- Zero-loss disaster recovery via journal replay

### 5. 🧠 Integrated Haven AI SDK (`haven_ai`)
Native streaming, reasoning extraction (`<think>` tag separation), model routing, and pipeline adapters:
```haven
from haven_ai import Client, pipe_fn

set client to Client()
set ai_engine to pipe_fn(client, model="meta-llama/Llama-3.3-70B-Instruct")

set response to "Synthesize local continuity theory" |> ai_engine
```

---

## 🚀 Unified Haven CLI (`haven`)

Haven includes a unified developer command suite available via `haven`, `haven.bat`, `haven.cmd`, and `haven.ps1`:

| Command | Description | Example |
| :--- | :--- | :--- |
| `haven run <file.hvn>` | Execute a Haven program (`.hvn`, `.haven`) | `haven run src/main.hvn --time` |
| `haven eval <code>` / `-c` | Directly evaluate Haven code strings | `haven -c "set x to 42; print(x)"` |
| `haven new <name>` | Scaffold complete ODCS applications & algorithm packages | `haven new MyLedgerApp --template odcs-app` |
| `haven test [path]` | Automated discovery & execution of test suites | `haven test tests/` |
| `haven check <file.hvn>` | Static syntax & ODCS contract integrity analysis | `haven check src/main.hvn` |
| `haven fmt <file.hvn>` | Code formatting & whitespace normalizer | `haven fmt src/main.hvn` |
| `haven repl` | Interactive Haven REPL with live ledger & benchmark tools | `haven repl` |
| `haven articles` | Read architectural essays & articles by the Creator | `haven articles read why-we-built-haven` |
| `haven odcs model` | Display the complete 4-Layer ODCS architectural model & invariants | `haven odcs model` |
| `haven odcs crdt` | Interactive CRDT multi-master state convergence demo | `haven odcs crdt` |
| `haven odcs tele` | Probe real-time network environmental telemetry & mode | `haven odcs tele` |
| `haven odcs live` | Launch live interactive browser dashboard on `http://localhost:8080` | `haven odcs live --port 8080` |
| `haven odcs export` | Export default ledger to standardized ODCS bundle | `haven odcs export ledger.odcs.json` |
| `haven odcs audit` | Cryptographic audit, journal replay, and inspection | `haven odcs audit journal.json` |
| `haven info` | Display Haven runtime architecture & specifications | `haven info` |
| `haven idle` | Launch the Haven Graphical IDE / Shell | `haven idle` |
| `haven --version` | Print Haven language version & ODCS specification | `haven --version` |

---

## 💻 Interactive Haven REPL

Launch the REPL with `haven repl`:

```text
╔═══════════════════════════════════════════════════════════════╗
║                    HAVEN LANGUAGE v1.0.0                      ║
║     Open Digital Continuity Standard (ODCS Edition)           ║
║        Specification & Architecture by Anirudha Puthraya      ║
╚═══════════════════════════════════════════════════════════════╝
Type :help for interactive commands, :syntax for cheat sheet, or :quit to exit.

haven ❯ set x to 10
haven ❯ repeat 3 times: set x to x * 2
haven ❯ x
⇒ 80
haven ❯ :bench [1, 2, 3, 4] |> len
Benchmark Result: 2.312 µs per run (1000 iterations)
haven ❯ :audit
✔ Default Ledger Chain AUDIT PASSED: 1 block(s) cryptographically verified.
```

### REPL Commands:
- `:help` — Comprehensive command guide
- `:syntax` — Complete Haven syntax cheatsheet
- `:model` / `:layers` — Display the formal 4-Layer ODCS architecture stack
- `:tele` — Probe live environmental network telemetry (RTT and Mode)
- `:crdt` — Demonstrate multi-master conflict-free convergence
- `:ledger` — Inspect active continuity ledger blocks
- `:audit` — Cryptographic proof verification of ledger chain
- `:vars` — List active session variables and types
- `:bench <code>` — High-precision statement/expression benchmarking
- `:info` — Runtime architecture & system specifications
- `:clear` — Clear terminal screen
- `:history` — Command history
- `:quit` / `:exit` — Exit REPL

---

## 🏗️ Project Scaffolding (`haven new`)

### Scaffold an ODCS Application System:
```bash
haven new BankingLedger --template odcs-app --author "Anirudha Puthraya"
```

Generates:
- `haven.toml`: Project manifest & continuity configuration
- `src/main.hvn`: Application entry point in native Haven
- `src/algorithm.hvn`: Continuity algorithm verifying state invariants
- `src/models.hvn`: Sealed domain records (`durable record`)
- `src/service.hvn`: High-level service wrapping `ODCSApp`
- `tests/test_app.hvn`: Comprehensive test suite
- `run.bat`: One-click execution launcher

### Scaffold an ODCS Continuity Algorithm Package:
```bash
haven new ConsensusEngine --template odcs-algorithm
```

---

## ☕ Java Enterprise Concepts & Annotations in Haven

Haven brings industrial Java-style rigor, strict contracts, and enterprise annotations to local-first, disruption-tolerant software:

### 1. 🏷️ Meta-Annotations & Reflection
Define custom type-safe annotations with `@interface`, `@Retention`, and `@Target`:
```haven
@interface
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
class EnterpriseEndpoint:
    path: str = ""
    auth_required: bool = True

class PaymentController:
    @EnterpriseEndpoint(path="/api/pay", auth_required=True)
    def handle_payment(self, req):
        return {"status": "authorized"}
```

### 2. 🔌 Java Interfaces with Default Methods (`@implements` & `@Override`)
Enforces compile-time and definition-time contract verification, with seamless inheritance of default methods:
```haven
class PaymentGateway(Interface):
    @abc.abstractmethod
    def process_payment(self, amount: float) -> str:
        pass

    @default
    def health_check(self) -> str:
        return "Gateway Online"

@implements(PaymentGateway)
class HavenStripeGateway:
    @Override
    def process_payment(self, amount: float) -> str:
        return f"Processed ${amount:.2f}"
```

### 3. 🛡️ Java 17 Sealed Classes (`permits=[...]`)
Strictly restrict which subclasses can extend your core hierarchy:
```haven
class ContinuityAsset(SealedClass, permits=["DurableCertificate", "MerkleProof"]):
    pass

class DurableCertificate(ContinuityAsset): # Allowed
    pass

class RogueAsset(ContinuityAsset): # Raises SealedHierarchyError!
    pass
```

### 4. 🔢 Rich Java-Style Enums (`HavenEnum`)
Enums with constructor parameters, state fields, ordinal indexing, and custom methods:
```haven
class LedgerNodeStatus(HavenEnum):
    ONLINE = (1, "Node is fully synchronized")
    DEGRADED = (2, "Operating in local partition mode")
    AIRGAPPED = (3, "Physical isolated operation")

    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description

    def is_operational(self) -> bool:
        return self.code in (1, 2)
```

### 5. ⚡ Enterprise Resilience & Concurrency Primitives
- **`@Transactional`**: Executes methods inside atomic WAL transactions with automatic rollback receipts on failure.
- **`@Audit`**: Cryptographically logs execution parameters, caller hashes, and execution duration to the Merkle ledger.
- **`@CircuitBreaker` & `@Retry`**: Prevents cascading failures with fast-fail circuit states (`CLOSED`, `OPEN`, `HALF_OPEN`) and exponential backoff retries.
- **`CompletableFuture`**: Java-style async pipeline chaining (`supply_async`, `then_apply`, `then_compose`, `all_of`).
- **`AtomicInteger`, `AtomicBoolean`, `AtomicReference`**: Lock-free CAS (Compare-And-Swap) variables.

---

## 💳 Open Financial Continuity Standard (OFCS-1.0.0)

**OFCS** is the financial-grade continuity framework authored by **Anirudha Puthraya**, establishing mathematically proven guarantees for sovereign banking, payments, and digital asset settlement:

### 1. 🪙 Exact Decimal Representation & Monetary Safety
Eliminates IEEE-754 floating-point drift (`0.10 + 0.20 == 0.30`) and enforces strict currency boundaries:
```haven
set m1 to Money("100.50", USD)
set m2 to Money("49.50", USD)
set total to m1 + m2 # Exactly $150.00 USD

set rate to ExchangeRate(USD, EUR, "0.92")
set eur_val to rate.convert(m1) # Exactly €92.46 EUR
```

### 2. ⚖️ Double-Entry Cryptographic Ledger
Every financial transaction strictly enforces **Invariant 1: Debits == Credits**:
```haven
set tx to DoubleEntryRecord(
    tx_id="tx-9901",
    debits=[("account_alice", Money("500.00", USD))],
    credits=[("account_bob", Money("500.00", USD))],
    memo="Payment for enterprise continuity license"
)
# Rejects unbalanced transactions with UnbalancedTransactionError!
```

### 3. 🔒 Financial Annotations
- **`@FinancialTransaction`**: Atomically debits/credits accounts with automatic rollback.
- **`@Idempotent`**: Replay-attack and double-spend shield; returns identical settled receipts for duplicate submissions.
- **`@ZeroDrift`**: Cryptographically asserts that the total monetary volume across all accounts is 100% conserved before and after execution.

### 4. 🌐 Distributed Offline Reconciliation Engine
Airgapped bank branches and edge POS terminals can transact offline and deterministically reconcile with central settlement hubs using Merkle difference trees:
```haven
set engine to ReconciliationEngine(federal_master_ledger)
set report to engine.reconcile_with_remote(branch_alaska_ledger)
print(f"Reconciliation Complete: {report.synced_successfully}")
```

---

## 🧪 Comprehensive Verification Suite

Haven features a built-in automated test suite:

```bash
haven test
```

Verifies:
- Natural English syntax assignments, loops, and guards
- Unary and chained pipeline operations (`|>`, `into`)
- Durable record immutability and tamper resistance
- Merkle root hashing and SHA-256 state digests
- Ledger checkpointing and cryptographic continuity chains
- Java-style Meta-Annotations, Interfaces, `@Override`, and Sealed Classes
- Enterprise Concurrency (`CompletableFuture`, `AtomicInteger`, CAS)
- Open Financial Continuity Standard (`Money`, Double-Entry, `@ZeroDrift`, `ReconciliationEngine`)
- Haven AI SDK streaming and reasoning extraction

---

## 📜 Standards & Architecture Attribution

- **Standard:** Open Digital Continuity Standard (ODCS-1.0.0)
- **Architecture & Specification Author:** Anirudha Puthraya
- **Organization:** Haven Language Foundation

---

*Haven Programming Language — Sovereign. Deterministic. Disruption-Tolerant.*

