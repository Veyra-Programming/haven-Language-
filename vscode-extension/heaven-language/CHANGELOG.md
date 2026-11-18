# Change Log

All notable changes to the **Haven Programming Language** extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-11-18

### Added
- **Ani++ Dual Identity & OmniEngine Architecture**:
  - Official language duality: **Ani++ / Haven** created by Anirudha Puthraya.
  - Dedicated `ani` CLI runner, `ani.bat`, and native `.ani`, `.ani++` source file execution.
- **World-First Concepts Introduced**:
  - **4D Chrono-Quantum Causality DAG & Timeline Rewind (`ChronoEngine`)**:
    - Native time-travel backwards (`chrono.rewind(steps)`), multiverse timeline branching (`chrono.fork("alternate")`), point-in-time travel (`chrono.travel_to(hash)`), and deterministic CRDT causal merge (`chrono.merge_branch()`).
    - **Quantum Speculative Execution (`chrono.speculate(fn)`)**: Zero-leak execution sandbox that automatically commits on success and completely annihilates on panic with zero state contamination.
  - **Polymorphic Entangled Memory Fabric (EMF)**:
    - 4 dimensional reality memory states: `Ephemeral` (RAM speed), `Durable` (Merkle WAL), `Entangled` (peer gossip mesh auto-sync), and `Synthesized` (dynamic cognitive reactivity).
    - `entangled(name, val)`: Distributed variables synchronized across nodes without network programming.
    - `synthesized(name, evaluator)`: Self-evaluating reactive variables.
    - `durable_var(name, val)`: Zero-crash-loss Merkle persisted variables.
  - **Autonomous Living Intent Reactor (Zero-Crash Invariant Defense)**:
    - `AutonomousHealer` / `heal()`: Autonomously intercepts fatal exceptions, evaluates declared invariants, synthesizes safe recovery trajectories (e.g. `CACHED_WAL_FALLBACK`), and mints cryptographic `HealingReceipt`s to maintain continuous uninterrupted uptime.
  - **AI-Symbiotic Cognitive Synthesis Reactor**:
    - Built-in zero-dependency 512-dimensional semantic vector generator (`deterministic_embedding`).
    - K-Nearest Neighbors vector search (`CognitiveReactor.search()`, `semantic_search()`), cosine similarity, Euclidean distance, and thought graph synthesis.
- **CLI & Developer Tooling Upgrades**:
  - `ani omni` / `haven omni`: High-tech visual status dashboard of 4D DAG, Healer, and Reality memory.
  - `ani timeline` / `haven timeline`: Visual terminal rendering of the 4D Chrono-Causality DAG tree.
  - `ani heal` / `haven heal`: Audit log of all autonomous self-healing incidents and cryptographic seal receipts.
- **Universal Import Hook**:
  - Direct cross-file imports for `.ani`, `.ani++`, `.hvn`, `.haven` files (e.g. `from src.main import ...`) powered by `HavenSourceLoader` and dynamic AST transpilation.

---

## [2.2.0] - 2026-11-13

### Added
- **Star Language Ergonomics & Dual-Grammar Engine**:
  - `use <module>` clean module imports side-by-side with `import`.
  - `variable <name> = <val>` mutable state variable declarations.
  - `constant <NAME> = <val>` immutable constant bindings.
  - `end` statement explicit block terminators for functions, conditionals, and loops.
  - Star arrow lambdas: `() -> expr` and `(x, y) -> expr`.
- **Active-Record `DurableModel` ORM**:
  - Full Active-Record pattern backed by the Open Digital Continuity Standard (ODCS).
  - Schema constraints via `Field(primary_key=True, unique=True, default=...)`.
  - O(1) in-memory primary key and indexed lookup: `.create()`, `.find()`, `.filter()`, `.all()`, `.count()`, `.update()`, `.delete()`.
  - 100% deterministic disaster recovery and audit replay via `.replay_from_ledger()`.
- **Advanced Backend & Microservices Suite**:
  - **In-Memory `TestClient`**: Zero-port direct HTTP request dispatcher for blazing-fast unit and integration testing.
  - **Turnkey OFCS Financial Vault**: Zero-boilerplate banking microservice endpoints (`/vault/accounts`, `/vault/transfers`, `/vault/audit`) enforcing Invariant 1 (Debits == Credits).
  - **Automated OpenAPI 3.0 & Dark-Mode Interactive Docs**: Auto-generated `/openapi.json` schema and turnkey `/docs` web GUI.
  - **Security Middlewares**: `APIKeyAuthMiddleware`, `BearerAuthMiddleware`, and `@require_auth` decorator.
  - **Asynchronous Worker Pool**: `BackgroundTaskPool` for non-blocking background task dispatching.
- **Extension Tooling & Intellisense**:
  - Added full autocompletions, type suggestions, hover documentation, and 12+ new signature entries for all Backend ORM and Star syntax constructs.
  - Added snippets for `use`, `variable`, `constant`, `end`, `durable-model`, `test-client`, and `mount-vault`.

---

## [2.1.0] - 2026-11-13

### Added
- **Intelligent Context-Aware Type Suggestions**:
  - Dynamically triggers type suggestions when typing colons (`:`), return type arrows (`->`), generic brackets (`[`), or defining fields in `durable record`.
  - Prioritizes types with top sorting in type annotation positions.
  - Comprehensive coverage across 6 type domains:
    - **Primitives**: `str`, `int`, `float`, `bool`, `bytes`, `bytearray`, `list`, `dict`, `set`, `tuple`, `Decimal`, `object`, `None`.
    - **Generics & Type Hints**: `Any`, `Optional[T]`, `Union[T1, T2]`, `List[T]`, `Dict[K, V]`, `Set[T]`, `Tuple[T, ...]`, `Callable`, `Type`, `Iterable`.
    - **ODCS Digital Continuity**: `DurableRecord`, `ContinuityLedger`, `LedgerEntry`, `MerkleTree`, `VectorClock`, `LWWRegister`, `PNCounter`, `AWORSet`, `OutboxPipeline`, `MeshNode`, `GossipMesh`, `ContinuityMode`, `EnvironmentalTelemetry`, `IntentReceipt`, `ZeroIntentLossManager`, `ContinuityAlgorithm`, `ODCSApp`.
    - **OFCS Financial Invariants**: `Money`, `Currency`, `ExchangeRate`, `DoubleEntryRecord`, `FinancialAccount`, `OFCSFinancialLedger`, `ReconciliationEngine`, `ReconciliationReport`.
    - **Enterprise Java Concurrency**: `Interface`, `SealedClass`, `HavenEnum`, `Record`, `TypeBound`, `GenericContainer`, `CompletableFuture`, `AtomicInteger`, `AtomicBoolean`, `AtomicReference`, `CountDownLatch`, `ReentrantLock`, `VirtualExecutor`.
    - **Backend Framework**: `HavenApp`, `HavenServer`, `Router`, `Request`, `Response`, `CORSMiddleware`, `ContinuityAuditMiddleware`, `RateLimiterMiddleware`.
- **Complete 59+ Signature Help Provider**:
  - Full parameter names, types, default values, and documentation triggered on `(` and `,`.
  - Active parameter position tracking with bracket-aware comma counting.
- **Official Haven Fox Mascot & Visual Branding**:
  - High-resolution glassmorphic 3D celestial cyber-fox mascot icons (`assets/logo.png`, `assets/fox_mascot.png`, `assets/file_icon.png`).
  - Dedicated VS Code status bar item (`🦊 Haven Fox`) with a 1-click action menu.
- **Enterprise Annotations & Snippets**:
  - Added snippets for typed functions (`def-typed`), typed bindings (`let-typed`, `set-typed`), typed records (`durable-typed`), and generics (`type-optional`, `type-list`, `type-dict`, `type-future`).
  - Added autocompletions for Java-style and ODCS annotations (`@Transactional`, `@CircuitBreaker`, `@Retry`, `@FinancialTransaction`, `@Idempotent`, `@ZeroDrift`, `@Override`, `@Sealed`, `@Audit`, `@ContinuityCheck`, `@Synchronized`, `@Volatile`, `@interface`, `@Retention`, `@Target`, `@Deprecated`).
- **Interactive Quick-Access Menu (`heaven.showMenu`)**:
  - Quick pick modal offering 1-click actions: Run File, Run Test Suite, Check Syntax, Compile to Bytecode, Launch Microservice Server, and Open Interactive REPL.

### Changed
- **Marketplace Publisher Alignment**:
  - Updated publisher identifier to `star-lang` in extension manifest for official Visual Studio Code Marketplace releases.
- **Multi-Language Document Selector**:
  - Activated extension language services seamlessly across both `haven` and `heaven` language identifiers as well as `.hvn`, `.haven`, and `.heaven` file patterns.

---

## [2.0.0] - 2026-11-13

### Added
- Initial release of Haven Programming Language (ODCS Native Edition).
- Natural English syntax grammar and TextMate grammar engine for `.hvn` and `.haven` files.
- Real-time AST linter and diagnostic error reporting in the Problems pane.
- Rich Markdown hover documentation for keywords (`set`, `let`, `remember`, `whenever`, `unless`, `until`, `repeat`, `give back`, `recover`, `ensure`, `say`, `show`, `checkpoint`, `preserve`, `verify`).
- Basic terminal runner and test suite integration.

