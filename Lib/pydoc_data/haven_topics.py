"""
Haven Programming Language (ODCS Native Edition) - Official Help Catalog
Architecture & Specification by Anirudha Puthraya
Standard: ODCS-1.0.0 & OFCS-1.0.0
"""

HAVEN_TOPICS = {
    # --- Control Flow & Natural English Keywords ---
    "set": """\
Haven Natural English Statement: set ... to
-------------------------------------------
Syntax:
    set <variable> to <expression>
    set <variable>: <type> to <expression>

Description:
    Declares or mutates variable state using natural English syntax.

Example:
    set active_nodes to 42
    set balance: Money to Money("100.00", USD)
""",

    "let": """\
Haven Natural English Statement: let ... be
-------------------------------------------
Syntax:
    let <variable> be <expression>
    let <variable>: <type> be <expression>

Description:
    Binds local variables in natural English.

Example:
    let discount_rate be 0.05
    let patient: DurableRecord be find_patient("PT-101")
""",

    "remember": """\
Haven Constant Declaration: remember ... as
-------------------------------------------
Syntax:
    remember <CONSTANT_NAME> as <expression>

Description:
    Binds an immutable constant value into the current namespace.

Example:
    remember STANDARD as "ODCS-1.0.0"
    remember MAX_CONNECTIONS as 1024
""",

    "increase": """\
Haven State Mutation: increase ... by
-------------------------------------
Syntax:
    increase <variable> by <delta>

Description:
    Increments a numeric variable by the specified delta.

Example:
    increase retry_attempts by 1
    increase total_score by points
""",

    "decrease": """\
Haven State Mutation: decrease ... by
-------------------------------------
Syntax:
    decrease <variable> by <delta>

Description:
    Decrements a numeric variable by the specified delta.

Example:
    decrease remaining_quota by 1
    decrease account_balance by withdrawal_amount
""",

    "whenever": """\
Haven Conditional Statement: whenever
-------------------------------------
Syntax:
    whenever <condition>:
        <block>
    otherwise if <condition>:
        <block>
    otherwise:
        <block>

Description:
    Natural English conditional branching statement.

Example:
    whenever balance >= amount:
        decrease balance by amount
        say "Transaction approved"
    otherwise if balance == 0:
        say "Account empty"
    otherwise:
        say "Insufficient funds"
""",

    "otherwise": """\
Haven Conditional Fallback: otherwise / otherwise if
----------------------------------------------------
Syntax:
    otherwise if <condition>:
    otherwise:

Description:
    Fallback branching for 'whenever' and 'unless' conditional blocks.
""",

    "unless": """\
Haven Inverted Conditional: unless
----------------------------------
Syntax:
    unless <condition>:
        <block>
    otherwise:
        <block>

Description:
    Executes the enclosed block when the given condition evaluates to false.

Example:
    unless network.is_online():
        switch_to_airgap_offline_mode()
""",

    "until": """\
Haven Loop Construct: until
---------------------------
Syntax:
    until <condition>:
        <block>

Description:
    Repeats execution of the enclosed block until the condition becomes true.

Example:
    until outbox.is_empty():
        flush_next_record()
""",

    "repeat": """\
Haven Loop Ergonomics: repeat ... times
---------------------------------------
Syntax:
    repeat <N> times:
        <block>

Description:
    Executes a loop block exactly N times without requiring an index variable.

Example:
    repeat 3 times:
        ping_cluster_node()
""",

    "forever": """\
Haven Event Loop: forever
-------------------------
Syntax:
    forever:
        <block>

Description:
    High-performance sub-millisecond infinite loop designed for microservices,
    daemon processes, and background event listeners.

Example:
    forever:
        poll_hardware_telemetry()
""",

    "give back": """\
Haven Subroutine Return: give back
----------------------------------
Syntax:
    give back <expression>
    give back

Description:
    Returns a computed value or terminates subroutine execution.

Example:
    define compute_checksum(data: bytes) -> str:
        give back seal_hash(data)
""",

    "give": """\
Haven Subroutine Return: give back
----------------------------------
Alias for 'give back'. See help('give back') for details.
""",

    "recover": """\
Haven Natural Exception Handling: recover as
--------------------------------------------
Syntax:
    try:
        <protected_block>
    recover as <err>:
        <recovery_block>
    always:
        <cleanup_block>

Description:
    Traps and inspects exceptions using natural English semantics, ensuring
    deterministic error recovery and cleanup.

Example:
    try:
        commit_to_ledger()
    recover as err:
        say "Error committing block:", err
    always:
        release_lock()
""",

    "ensure": """\
Haven Invariant Assertion: ensure ... otherwise
-----------------------------------------------
Syntax:
    ensure <condition> otherwise "<error_message>"

Description:
    Validates architectural and domain invariants. If condition is false,
    raises a ContinuityInvariantError with the custom message.

Example:
    ensure sum(debits) == sum(credits) otherwise "Unbalanced transaction error"
""",

    "say": """\
Haven Output Statement: say
---------------------------
Syntax:
    say <expression>

Description:
    Prints formatted expression output to the standard output console.

Example:
    say "Server running on port {port}"
""",

    "show": """\
Haven Inspection Statement: show
--------------------------------
Syntax:
    show <expression>

Description:
    Prints debug and structural inspection details of an object or expression.

Example:
    show ledger.head_hash
""",

    "pipe": """\
Haven Functional Pipeline: |>
-----------------------------
Syntax:
    <value> |> <func1> |> <func2>
    <value> |> <func>(arg1, _, arg2)

Description:
    Unix-style pipeline passing the output of one function as the argument to the next.
    Supports placeholder `_` for positional argument control.

Example:
    "haven architecture" |> str.upper |> say
    10 |> pow(2, _) |> say  # 2 ** 10 = 1024
""",

    "define": """\
Haven Function Definition: define / function
--------------------------------------------
Syntax:
    define <func_name>(<param>: <type>) -> <return_type>:
        <block>

Description:
    Declares a strongly-typed or dynamic Haven function or method.

Example:
    define verify_record(rec: DurableRecord) -> bool:
        give back rec.is_sealed
""",

    # --- ODCS Digital Continuity Standards ---
    "durable": """\
Haven ODCS Construct: durable record
------------------------------------
Syntax:
    durable record <RecordName>:
        <field1>: <type1>
        <field2>: <type2>

Description:
    Declares an immutable, schema-enforced state record. Automatically equips
    the class with RFC 8785 canonical JSON serialization, cryptographic SHA-256
    seals, and tamper-evident write-ahead logging (WAL) support.

Example:
    durable record PatientVitals:
        patient_id: str
        heart_rate: int
        blood_pressure: str
        is_stable: bool
""",

    "checkpoint": """\
Haven ODCS Statement: checkpoint
--------------------------------
Syntax:
    checkpoint <asset> as "<alias>" into <ledger>

Description:
    Atomically commits the state of an asset or durable record into an append-only
    cryptographic ledger with Merkle DAG validation and head hash computation.

Example:
    checkpoint vitals as "admission_triage" into primary_ledger
""",

    "preserve": """\
Haven ODCS Invariant Statement: preserve
----------------------------------------
Syntax:
    preserve <payload> as "<alias>" into <ledger>

Description:
    ODCS Layer 4 Invariant: Mints a local tamper-evident intent receipt in <16ms,
    guaranteeing Zero Intent Loss during airgap offline states or sudden crashes.

Example:
    preserve click_event as "checkout_intent" into outbox_ledger
""",

    "verify": """\
Haven ODCS Invariant Statement: verify
--------------------------------------
Syntax:
    verify <asset> with <proof>

Description:
    Cryptographically verifies SHA-256 Merkle proofs against the ledger head hash,
    proving data authenticity and immutability with mathematical certainty.

Example:
    whenever verify asset with proof:
        say "Asset verified intact"
""",

    "ODCS": """\
Open Digital Continuity Standard (ODCS)
---------------------------------------
Standard Specification & Architecture by Anirudha Puthraya.
Governs high-reliability systems across intermittent networks and airgap offline states.

The 4 ODCS Layers:
    1. Layer 1 (Storage): Local Durability, WAL, Binary Merkle DAG Root validation.
    2. Layer 2 (Transport): Vector Clock partial ordering, CRDT consensus (PN-Counter, AW-ORSet).
    3. Layer 3 (Runtime): Environmental Telemetry, automatic Airgap offline degradation.
    4. Layer 4 (Application): Zero Intent Loss, sub-16ms local authority receipt minting.

Specification & Reference: https://github.com/Veyra-Programming/haven-Language-
""",

    "OFCS": """\
Open Financial Continuity Standard (OFCS)
-----------------------------------------
Standard Specification & Architecture by Anirudha Puthraya.
Financial extension to ODCS ensuring mathematical exactness and fraud prevention.

Core Invariants:
    - Zero Drift: Exact arbitrary-precision Decimal arithmetic (no float rounding loss).
    - Currency Safety: Strict ISO-4217 currency tagging and atomic conversions.
    - Invariant 1 (Double-Entry Balance): sum(debits) MUST EQUAL sum(credits).
    - Distributed Offline Reconciliation: Deterministic branch convergence.
""",

    "Money": """\
OFCS Invariant Type: Money
--------------------------
Syntax:
    Money(amount: Union[str, int, float, Decimal], currency: Currency = USD)

Description:
    Zero-drift decimal currency representation with exact monetary arithmetic.
    Prevents floating-point precision loss and protects cross-currency transactions.

Example:
    set price to Money("199.99", USD)
    set total to price + Money("50.00", USD)
""",

    "DoubleEntryRecord": """\
OFCS Invariant 1: DoubleEntryRecord
-----------------------------------
Syntax:
    DoubleEntryRecord(tx_id: str, debits: List[Money], credits: List[Money], description: str = "")

Description:
    Enforces fundamental accounting equality: sum(debits) == sum(credits).
    Attempting to construct or post an unbalanced transaction raises InvariantViolationError.

Example:
    set tx to DoubleEntryRecord(
        tx_id="TX-1001",
        debits=[Money("100.00", USD)],
        credits=[Money("100.00", USD)],
        description="Invoice payment"
    )
""",

    "ContinuityLedger": """\
ODCS Layer 1: ContinuityLedger
------------------------------
Syntax:
    ContinuityLedger(name: str = "primary", storage_path: str = None)

Description:
    Append-only cryptographic write-ahead log (WAL) and Merkle DAG calculating
    tamper-evident continuity root hashes. Supports journal replay and disaster recovery.

Example:
    set ledger to ContinuityLedger("vault")
    set entry to ledger.append({"record_id": "REC-01", "status": "SEALED"})
""",

    "HavenApp": """\
Haven Backend Container: HavenApp
---------------------------------
Syntax:
    HavenApp(name="HavenService", host="127.0.0.1", port=8080, cors=True, continuity_audit=True)

Description:
    Enterprise microservice container featuring declarative routing, CORS,
    sliding-window rate limiting, and pre-built ODCS/OFCS audit REST endpoints.

Example:
    app = HavenApp(name="Gateway", port=8080)

    @app.get("/api/v1/health")
    def health(req: Request) -> Response:
        give back Response.ok("Service healthy")

    app.run(blocking=True)
""",

    "HavenServer": """\
Haven Backend: HavenServer
--------------------------
Syntax:
    HavenServer(host="127.0.0.1", port=8080, router=None)

Description:
    High-performance concurrent multi-threaded HTTP server powering HavenApp.
""",

    "Router": """\
Haven Backend: Router
---------------------
Syntax:
    Router()

Description:
    Declarative HTTP router supporting path templates (e.g. /users/{user_id}),
    method routing (@router.get, @router.post), and middleware cascades.
""",

    "CompletableFuture": """\
Java Concurrency: CompletableFuture[T]
--------------------------------------
Syntax:
    CompletableFuture.supply_async(supplier, executor=None)
    CompletableFuture.run_async(runnable, executor=None)

Description:
    Non-blocking reactive promise pipeline for asynchronous task composition
    supporting then_apply, then_compose, and exceptionally handlers.

Example:
    CompletableFuture.supply_async(lambda: fetch_data()) \\
        .then_apply(lambda data: process(data)) \\
        .then_accept(lambda res: say "Result:", res)
""",

    "AtomicInteger": """\
Java Concurrency: AtomicInteger
-------------------------------
Syntax:
    AtomicInteger(initial_value: int = 0)

Description:
    Lock-free atomic integer supporting compare_and_set, increment_and_get,
    and decrement_and_get operations.

Example:
    set counter to AtomicInteger(0)
    counter.increment_and_get()
"""
}

# Aliases for convenience
HAVEN_TOPICS["HAVEN_SET"] = HAVEN_TOPICS["set"]
HAVEN_TOPICS["HAVEN_LET"] = HAVEN_TOPICS["let"]
HAVEN_TOPICS["HAVEN_REMEMBER"] = HAVEN_TOPICS["remember"]
HAVEN_TOPICS["HAVEN_INCREASE"] = HAVEN_TOPICS["increase"]
HAVEN_TOPICS["HAVEN_DECREASE"] = HAVEN_TOPICS["decrease"]
HAVEN_TOPICS["HAVEN_WHENEVER"] = HAVEN_TOPICS["whenever"]
HAVEN_TOPICS["HAVEN_OTHERWISE"] = HAVEN_TOPICS["otherwise"]
HAVEN_TOPICS["HAVEN_UNLESS"] = HAVEN_TOPICS["unless"]
HAVEN_TOPICS["HAVEN_UNTIL"] = HAVEN_TOPICS["until"]
HAVEN_TOPICS["HAVEN_REPEAT"] = HAVEN_TOPICS["repeat"]
HAVEN_TOPICS["HAVEN_FOREVER"] = HAVEN_TOPICS["forever"]
HAVEN_TOPICS["HAVEN_GIVE_BACK"] = HAVEN_TOPICS["give back"]
HAVEN_TOPICS["HAVEN_RECOVER"] = HAVEN_TOPICS["recover"]
HAVEN_TOPICS["HAVEN_ENSURE"] = HAVEN_TOPICS["ensure"]
HAVEN_TOPICS["HAVEN_SAY"] = HAVEN_TOPICS["say"]
HAVEN_TOPICS["HAVEN_SHOW"] = HAVEN_TOPICS["show"]
HAVEN_TOPICS["HAVEN_CHECKPOINT"] = HAVEN_TOPICS["checkpoint"]
HAVEN_TOPICS["HAVEN_PRESERVE"] = HAVEN_TOPICS["preserve"]
HAVEN_TOPICS["HAVEN_VERIFY"] = HAVEN_TOPICS["verify"]
HAVEN_TOPICS["HAVEN_DURABLE"] = HAVEN_TOPICS["durable"]
HAVEN_TOPICS["HAVEN_INTO"] = HAVEN_TOPICS["into"] = HAVEN_TOPICS["pipe"]
HAVEN_TOPICS["HAVEN_PIPE"] = HAVEN_TOPICS["pipe"]
HAVEN_TOPICS["HAVEN_DEFINE"] = HAVEN_TOPICS["define"]
HAVEN_TOPICS["HAVEN_ODCS"] = HAVEN_TOPICS["ODCS"]
HAVEN_TOPICS["HAVEN_OFCS"] = HAVEN_TOPICS["OFCS"]
HAVEN_TOPICS["HAVEN_MONEY"] = HAVEN_TOPICS["Money"]
HAVEN_TOPICS["HAVEN_DOUBLEENTRY"] = HAVEN_TOPICS["DoubleEntryRecord"]
HAVEN_TOPICS["HAVEN_CONTINUITY"] = HAVEN_TOPICS["ContinuityLedger"]
HAVEN_TOPICS["HAVEN_BACKEND"] = HAVEN_TOPICS["HavenApp"]
HAVEN_TOPICS["HAVEN_CONCURRENCY"] = HAVEN_TOPICS["CompletableFuture"]
