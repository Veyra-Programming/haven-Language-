# Change Log

All notable changes to the **Haven Programming Language** extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

