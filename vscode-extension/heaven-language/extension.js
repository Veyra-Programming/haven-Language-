/**
 * 🦊 Haven Programming Language (ODCS Native Edition) - Visual Studio Code Extension
 * 
 * Features:
 *  - Official Haven Fox Mascot & Visual Branding
 *  - Comprehensive Type Suggestions for Primitives, Generics, ODCS, OFCS & Enterprise Types
 *  - Context-Aware Autocompletion for Type Annotations, Colons (:), Return Types (->) & Generics ([])
 *  - Real-Time AST Linting & Error Diagnostics
 *  - Contextual Hover Tooltips with Keyword Uses, Type Invariants & Signatures
 *  - Complete 59+ Signature Help Provider for Builtins, Types & Concurrency
 *  - 1-Click Terminal Execution & Test Suite Runner
 * 
 * Architect: Anirudha Puthraya · Standard: ODCS-1.0.0 & OFCS-1.0.0
 * Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
 */

const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');
const fs = require('fs');

let diagnosticCollection;
let havenStatusBarItem;

const HAVEN_SELECTOR = [
    { language: 'haven' },
    { language: 'heaven' },
    { pattern: '**/*.hvn' },
    { pattern: '**/*.haven' },
    { pattern: '**/*.heaven' }
];

/**
 * Locate the Haven runner and executable.
 */
function getHavenRunnerInfo() {
    const config = vscode.workspace.getConfiguration('heaven');
    const customRunner = config.get('runnerPath');
    if (customRunner && fs.existsSync(customRunner)) {
        return { runner: customRunner, havenExe: customRunner };
    }

    const appDataHaven = path.join(
        process.env.LOCALAPPDATA || '',
        'Programs', 'Haven', 'haven.exe'
    );
    if (fs.existsSync(appDataHaven)) {
        return { runner: appDataHaven, havenExe: appDataHaven };
    }

    const workspaceFolders = vscode.workspace.workspaceFolders || [];
    for (const folder of workspaceFolders) {
        const buildHaven = path.join(folder.uri.fsPath, 'PCbuild', 'amd64', 'haven.exe');
        if (fs.existsSync(buildHaven)) {
            return { runner: buildHaven, havenExe: buildHaven };
        }
        const havenBat = path.join(folder.uri.fsPath, 'haven.bat');
        if (fs.existsSync(havenBat)) {
            return { runner: havenBat, havenExe: havenBat };
        }
    }

    return { runner: 'haven', havenExe: 'haven' };
}

/**
 * Run command in a dedicated VS Code terminal.
 */
function runInTerminal(terminalName, command) {
    let term = vscode.window.terminals.find(t => t.name === terminalName);
    if (!term) {
        term = vscode.window.createTerminal(terminalName);
    }
    term.show(true);
    term.sendText(command);
}

/**
 * Run syntax diagnostics using haven lint.
 */
function validateDocument(document) {
    if (document.languageId !== 'heaven' && document.languageId !== 'haven' &&
        !document.fileName.endsWith('.hvn') && !document.fileName.endsWith('.haven')) {
        return;
    }

    const { havenExe } = getHavenRunnerInfo();
    const filePath = document.fileName;

    cp.exec(`"${havenExe}" -m haven.cli check "${filePath}"`, (err, stdout, stderr) => {
        const diagnostics = [];
        const combined = (stderr || '') + '\n' + (stdout || '');

        const errMatch = combined.match(/\[Haven SyntaxError\]\s+line\s+(\d+):\s+(.+)/i) ||
                         combined.match(/SyntaxError:\s+(.+?)\s+\[Line\s+(\d+)/i) ||
                         combined.match(/Line\s+(\d+).*?Error:\s+(.+)/i);
        if (errMatch) {
            let lineNum = 0;
            let message = "Syntax Error";
            if (errMatch[2] && !isNaN(parseInt(errMatch[1], 10))) {
                lineNum = Math.max(0, parseInt(errMatch[1], 10) - 1);
                message = errMatch[2].trim();
            } else if (errMatch[2] && !isNaN(parseInt(errMatch[2], 10))) {
                lineNum = Math.max(0, parseInt(errMatch[2], 10) - 1);
                message = errMatch[1].trim();
            }
            const lineText = document.lineAt(Math.min(lineNum, document.lineCount - 1)).text;
            const startChar = lineText.search(/\S/);
            const range = new vscode.Range(lineNum, Math.max(0, startChar), lineNum, lineText.length);
            const diagnostic = new vscode.Diagnostic(range, `[Haven Syntax] ${message}`, vscode.DiagnosticSeverity.Error);
            diagnostic.source = 'Haven Fox Linter';
            diagnostics.push(diagnostic);
        }

        diagnosticCollection.set(document.uri, diagnostics);
    });
}

/**
 * Complete Type Suggestions Catalog
 * Categorized into Primitives, Generics, ODCS, OFCS, Enterprise & Backend Types
 */
const HAVEN_TYPE_ITEMS = [
    // --- Built-in Primitives ---
    {
        label: 'str',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Immutable UTF-8 String Sequence',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `str`**\n\nImmutable UTF-8 text string sequence.\n\n*Example:*\n```haven\nlet title: str be "Haven Architecture"\n```')
    },
    {
        label: 'int',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • 64-bit Arbitrary-Precision Integer',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `int`**\n\nArbitrary-precision integer number.\n\n*Example:*\n```haven\nset count: int to 100\n```')
    },
    {
        label: 'float',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • IEEE 754 Double-Precision Float',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `float`**\n\nDouble-precision floating point number.\n\n*Example:*\n```haven\nlet ratio: float be 3.14159\n```')
    },
    {
        label: 'bool',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Boolean Flag (true / false)',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `bool`**\n\nBoolean truth value (`true` or `false`).\n\n*Example:*\n```haven\nset is_verified: bool to true\n```')
    },
    {
        label: 'bytes',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Immutable Byte Buffer',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `bytes`**\n\nImmutable raw byte buffer for binary protocols and SHA-256 hashes.\n\n*Example:*\n```haven\nlet raw_hash: bytes be b"sha256-digest"\n```')
    },
    {
        label: 'bytearray',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Mutable Byte Buffer',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `bytearray`**\n\nMutable byte array for low-level packet buffer manipulation.')
    },
    {
        label: 'list',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Dynamic Ordered Array',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `list`**\n\nDynamic resizable array sequence.\n\n*Example:*\n```haven\nset items: list to [1, 2, 3]\n```')
    },
    {
        label: 'dict',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Key-Value Hash Map',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `dict`**\n\nAssociative key-value hash mapping table.\n\n*Example:*\n```haven\nlet headers: dict be {"Content-Type": "application/json"}\n```')
    },
    {
        label: 'set',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Unordered Unique Collection',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `set`**\n\nUnordered collection of unique items.\n\n*Example:*\n```haven\nset unique_keys: set to {1, 2, 3}\n```')
    },
    {
        label: 'tuple',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Fixed Immutable Sequence',
        documentation: new vscode.MarkdownString('**Haven Primitive Type: `tuple`**\n\nFixed-size immutable sequence.\n\n*Example:*\n```haven\nlet pair: tuple be ("key", 42)\n```')
    },
    {
        label: 'Decimal',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Exact Fixed-Point Decimal',
        documentation: new vscode.MarkdownString('**Haven Numeric Type: `Decimal`**\n\nArbitrary-precision decimal arithmetic without floating-point drift.\n\n*Example:*\n```haven\nlet val: Decimal be Decimal("100.50")\n```')
    },
    {
        label: 'object',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Root Type',
        documentation: new vscode.MarkdownString('**Haven Type: `object`**\n\nThe fundamental base type for all Haven classes.')
    },
    {
        label: 'None',
        kind: vscode.CompletionItemKind.Class,
        detail: 'primitive type • Unit Null Type (nothing)',
        documentation: new vscode.MarkdownString('**Haven Primitive: `None` / `nothing`**\n\nRepresents the absence of a value or void return type.')
    },

    // --- Type Hinting & Generics ---
    {
        label: 'Any',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Unconstrained Dynamic Type',
        documentation: new vscode.MarkdownString('**Type Hint: `Any`**\n\nMatches any arbitrary value without static type restriction.')
    },
    {
        label: 'Optional',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Optional[T] (T or None)',
        insertText: new vscode.SnippetString('Optional[${1:T}]'),
        documentation: new vscode.MarkdownString('**Type Hint: `Optional[T]`**\n\nShorthand for `Union[T, None]` indicating a nullable value.\n\n*Example:*\n```haven\ndef find_asset(id: str) -> Optional[DurableRecord]:\n```')
    },
    {
        label: 'Union',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Union[T1, T2]',
        insertText: new vscode.SnippetString('Union[${1:T1}, ${2:T2}]'),
        documentation: new vscode.MarkdownString('**Type Hint: `Union[T1, T2]`**\n\nIndicates a value can be of type `T1` or `T2`.')
    },
    {
        label: 'List',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • List[T]',
        insertText: new vscode.SnippetString('List[${1:T}]'),
        documentation: new vscode.MarkdownString('**Type Hint: `List[T]`**\n\nHomogeneous list of elements of type `T`.\n\n*Example:*\n```haven\nlet entries: List[LedgerEntry] be []\n```')
    },
    {
        label: 'Dict',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Dict[KeyType, ValueType]',
        insertText: new vscode.SnippetString('Dict[${1:str}, ${2:Any}]'),
        documentation: new vscode.MarkdownString('**Type Hint: `Dict[K, V]`**\n\nTyped dictionary with keys of type `K` and values of type `V`.')
    },
    {
        label: 'Set',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Set[T]',
        insertText: new vscode.SnippetString('Set[${1:T}]'),
        documentation: new vscode.MarkdownString('**Type Hint: `Set[T]`**\n\nTyped set containing unique items of type `T`.')
    },
    {
        label: 'Tuple',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Tuple[T, ...]',
        insertText: new vscode.SnippetString('Tuple[${1:T}, ...]'),
        documentation: new vscode.MarkdownString('**Type Hint: `Tuple[T, ...]`**\n\nTyped tuple with specified positional types.')
    },
    {
        label: 'Callable',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Callable[[Args], ReturnType]',
        insertText: new vscode.SnippetString('Callable[[${1:Args}], ${2:ReturnType}]'),
        documentation: new vscode.MarkdownString('**Type Hint: `Callable[[Args], ReturnType]`**\n\nFunction or subroutine reference signature.')
    },
    {
        label: 'Type',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Type[T] (Class Reference)',
        insertText: new vscode.SnippetString('Type[${1:T}]'),
        documentation: new vscode.MarkdownString('**Type Hint: `Type[T]`**\n\nReference to a class definition itself.')
    },
    {
        label: 'Iterable',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'typing • Iterable[T]',
        insertText: new vscode.SnippetString('Iterable[${1:T}]'),
        documentation: new vscode.MarkdownString('**Type Hint: `Iterable[T]`**\n\nSequence or generator yielding values of type `T`.')
    },

    // --- ODCS Digital Continuity Types ---
    {
        label: 'DurableRecord',
        kind: vscode.CompletionItemKind.Struct,
        detail: 'type (ODCS Layer 1) • Cryptographically Sealed Record',
        documentation: new vscode.MarkdownString('**ODCS Type: `DurableRecord`**\n\nImmutable state record with deterministic RFC 8785 canonical JSON serialization and SHA-256 seal hashing.\n\n*Example:*\n```haven\ndurable record PatientTriage:\n    patient_id: str\n    heart_rate: int\n    triage_notes: str\n```')
    },
    {
        label: 'ContinuityLedger',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 1) • Append-Only Cryptographic Merkle Ledger',
        documentation: new vscode.MarkdownString('**ODCS Type: `ContinuityLedger`**\n\nLocal append-only write-ahead log (WAL) and Merkle DAG calculating tamper-evident continuity roots.\n\n*Example:*\n```haven\nset ledger to ContinuityLedger("vital_records")\n```')
    },
    {
        label: 'LedgerEntry',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 1) • Immutable Ledger Block Entry',
        documentation: new vscode.MarkdownString('**ODCS Type: `LedgerEntry`**\n\nSingle block entry containing timestamp, previous hash, entry hash, and canonical payload.')
    },
    {
        label: 'MerkleTree',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 1) • Binary Cryptographic Merkle Tree',
        documentation: new vscode.MarkdownString('**ODCS Type: `MerkleTree`**\n\nBinary cryptographic tree producing proof paths and head hash validation.')
    },
    {
        label: 'VectorClock',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 2) • Distributed Causality Frontier',
        documentation: new vscode.MarkdownString('**ODCS Type: `VectorClock`**\n\nTracks Lamport causality timestamps across decentralized nodes.')
    },
    {
        label: 'PNCounter',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 2) • Positive-Negative Counter CRDT',
        documentation: new vscode.MarkdownString('**ODCS Type: `PNCounter`**\n\nConflict-Free Replicated Data Type ensuring deterministic convergence across network partitions.')
    },
    {
        label: 'AWORSet',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 2) • Add-Wins Observed-Removed Set CRDT',
        documentation: new vscode.MarkdownString('**ODCS Type: `AWORSet`**\n\nCRDT collection that cleanly resolves concurrent additions and removals.')
    },
    {
        label: 'LWWRegister',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 2) • Last-Write-Wins Register CRDT',
        documentation: new vscode.MarkdownString('**ODCS Type: `LWWRegister`**\n\nConflict-Free Replicated Data Type utilizing timestamped causality.')
    },
    {
        label: 'OutboxPipeline',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 2) • Store-and-Forward Outbox Pipeline',
        documentation: new vscode.MarkdownString('**ODCS Type: `OutboxPipeline`**\n\nGuarantees monotonic queuing and delivery acknowledgement across network reconnects.')
    },
    {
        label: 'MeshNode',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 2) • P2P Mesh Participant Node',
        documentation: new vscode.MarkdownString('**ODCS Type: `MeshNode`**\n\nDecentralized peer node participating in gossip replication.')
    },
    {
        label: 'GossipMesh',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 2) • Epidemic Dissemination Network',
        documentation: new vscode.MarkdownString('**ODCS Type: `GossipMesh`**\n\nDecentralized peer-to-peer gossip dissemination mesh.')
    },
    {
        label: 'ContinuityMode',
        kind: vscode.CompletionItemKind.Enum,
        detail: 'type (ODCS Layer 3) • Connectivity State Enum',
        documentation: new vscode.MarkdownString('**ODCS Type: `ContinuityMode`**\n\nEnumeration: `OFFLINE_AIRGAP`, `STORE_FORWARD`, `FULL_CONNECTIVITY`.')
    },
    {
        label: 'EnvironmentalTelemetry',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 3) • Runtime Environmental Prober',
        documentation: new vscode.MarkdownString('**ODCS Type: `EnvironmentalTelemetry`**\n\nMonitors network availability, latency, and power budget.')
    },
    {
        label: 'IntentReceipt',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 4) • Zero-Intent-Loss Proof Receipt',
        documentation: new vscode.MarkdownString('**ODCS Type: `IntentReceipt`**\n\nCryptographic receipt minted within <16ms confirming local preservation.')
    },
    {
        label: 'ZeroIntentLossManager',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 4) • Sub-16ms Local Preservation Gateway',
        documentation: new vscode.MarkdownString('**ODCS Type: `ZeroIntentLossManager`**\n\nEnsures zero lost user actions during crashes, airgap mode, or network failures.')
    },
    {
        label: 'ContinuityAlgorithm',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS Layer 1) • Deterministic State Machine Base',
        documentation: new vscode.MarkdownString('**ODCS Type: `ContinuityAlgorithm`**\n\nBase class providing deterministic state transitions and complete journal replay.')
    },
    {
        label: 'ODCSApp',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (ODCS) • Enterprise Application Container',
        documentation: new vscode.MarkdownString('**ODCS Type: `ODCSApp`**\n\nIntegrated ODCS application container with automatic continuity gateway.')
    },

    // --- OFCS Financial Continuity Types ---
    {
        label: 'Money',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (OFCS Invariant) • Exact Decimal Currency with Zero Drift',
        insertText: new vscode.SnippetString('Money("${1:100.00}", ${2:USD})'),
        documentation: new vscode.MarkdownString('**OFCS Invariant Type: `Money`**\n\nStrict decimal currency representation with exact mathematical arithmetic and currency safety.\n\n*Example:*\n```haven\nset price: Money to Money("250.00", USD)\n```')
    },
    {
        label: 'Currency',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (OFCS Invariant) • ISO-4217 Currency Descriptor',
        documentation: new vscode.MarkdownString('**OFCS Type: `Currency`**\n\nISO-4217 currency descriptor with strict precision boundaries (`USD`, `EUR`, `GBP`, `INR`, `JPY`, `BTC`, `HVN`).')
    },
    {
        label: 'ExchangeRate',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (OFCS Invariant) • Deterministic Exchange Multiplier',
        documentation: new vscode.MarkdownString('**OFCS Type: `ExchangeRate`**\n\nAtomic exchange rate multiplier preventing rounding loss across currency conversions.')
    },
    {
        label: 'DoubleEntryRecord',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (OFCS Invariant 1) • Debits == Credits Balanced Transaction',
        insertText: new vscode.SnippetString('DoubleEntryRecord("${1:TX-1001}", debits=[${2:m1}], credits=[${3:m2}])'),
        documentation: new vscode.MarkdownString('**OFCS Invariant 1: `DoubleEntryRecord`**\n\nEnforces mathematical double-entry balance: `sum(debits) == sum(credits)`. Prevents financial fraud and unbalanced ledgers.')
    },
    {
        label: 'FinancialAccount',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (OFCS Invariant) • Audited Balance Account',
        documentation: new vscode.MarkdownString('**OFCS Type: `FinancialAccount`**\n\nDouble-entry balance account with immutable audit trail and overdraft controls.')
    },
    {
        label: 'OFCSFinancialLedger',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (OFCS Invariant) • Tamper-Evident Financial Journal',
        documentation: new vscode.MarkdownString('**OFCS Type: `OFCSFinancialLedger`**\n\nAppend-only financial ledger with WAL commit log and double-entry invariants.')
    },
    {
        label: 'ReconciliationEngine',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (OFCS) • Distributed Offline Financial Reconciler',
        documentation: new vscode.MarkdownString('**OFCS Type: `ReconciliationEngine`**\n\nReconciles offline financial ledger branches with mathematical zero loss.')
    },
    {
        label: 'ReconciliationReport',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (OFCS) • Ledger Reconciliation Summary',
        documentation: new vscode.MarkdownString('**OFCS Type: `ReconciliationReport`**\n\nAudit summary report containing verified entries and discrepancies.')
    },

    // --- Haven Enterprise & Java Concurrency Types ---
    {
        label: 'Interface',
        kind: vscode.CompletionItemKind.Interface,
        detail: 'type (Enterprise) • Java-Style Contract Interface',
        documentation: new vscode.MarkdownString('**Java Enterprise Concept: `Interface`**\n\nDefines strict method contracts and default method implementations with `@implements` enforcement.')
    },
    {
        label: 'SealedClass',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Enterprise) • Java 17 Sealed Class Hierarchy',
        documentation: new vscode.MarkdownString('**Java Enterprise Concept: `SealedClass`**\n\nRestricts inheritance hierarchy strictly to permitted subclasses declared via `@Sealed(permits=(...))`.')
    },
    {
        label: 'HavenEnum',
        kind: vscode.CompletionItemKind.Enum,
        detail: 'type (Enterprise) • Rich Java Enum with Constructors & Methods',
        documentation: new vscode.MarkdownString('**Java Enterprise Concept: `HavenEnum`**\n\nRich enum with custom constructor arguments, properties, and methods.')
    },
    {
        label: 'Record',
        kind: vscode.CompletionItemKind.Struct,
        detail: 'type (Enterprise) • Transparent Data Carrier',
        documentation: new vscode.MarkdownString('**Java Enterprise Concept: `Record`**\n\nTransparent, immutable data carrier with auto-generated equality and hash codes.')
    },
    {
        label: 'TypeBound',
        kind: vscode.CompletionItemKind.TypeParameter,
        detail: 'type (Enterprise) • Generic Type Constraint',
        documentation: new vscode.MarkdownString('**Java Enterprise Concept: `TypeBound`**\n\nEnforces type boundary rules on generic arguments.')
    },
    {
        label: 'GenericContainer',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Enterprise) • Strongly-Typed Container',
        documentation: new vscode.MarkdownString('**Java Enterprise Concept: `GenericContainer[T]`**\n\nRuntime-verified generic container.')
    },
    {
        label: 'CompletableFuture',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Java Concurrency) • Non-Blocking Reactive Promise',
        insertText: new vscode.SnippetString('CompletableFuture.supply_async(lambda: ${1:computation()})'),
        documentation: new vscode.MarkdownString('**Java Concurrency: `CompletableFuture[T]`**\n\nReactive, non-blocking promise pipeline for asynchronous task composition with `then_apply`, `then_compose`, and `exceptionally`.')
    },
    {
        label: 'AtomicInteger',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Java Concurrency) • Lock-Free CAS Integer',
        insertText: new vscode.SnippetString('AtomicInteger(${1:0})'),
        documentation: new vscode.MarkdownString('**Java Concurrency: `AtomicInteger`**\n\nLock-free atomic integer supporting compare_and_set, increment_and_get, and decrement_and_get.')
    },
    {
        label: 'AtomicBoolean',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Java Concurrency) • Lock-Free CAS Boolean',
        insertText: new vscode.SnippetString('AtomicBoolean(${1:false})'),
        documentation: new vscode.MarkdownString('**Java Concurrency: `AtomicBoolean`**\n\nLock-free atomic boolean supporting atomic toggle and CAS.')
    },
    {
        label: 'AtomicReference',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Java Concurrency) • Lock-Free Object Pointer',
        insertText: new vscode.SnippetString('AtomicReference(${1:None})'),
        documentation: new vscode.MarkdownString('**Java Concurrency: `AtomicReference[T]`**\n\nLock-free atomic object reference with compare_and_set.')
    },
    {
        label: 'CountDownLatch',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Java Concurrency) • Thread Synchronization Barrier',
        insertText: new vscode.SnippetString('CountDownLatch(${1:1})'),
        documentation: new vscode.MarkdownString('**Java Concurrency: `CountDownLatch`**\n\nSynchronization barrier that blocks threads until count reaches zero.')
    },
    {
        label: 'ReentrantLock',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Java Concurrency) • Reentrant Mutual Exclusion Lock',
        documentation: new vscode.MarkdownString('**Java Concurrency: `ReentrantLock`**\n\nReentrant mutual exclusion lock supporting `try_lock` with timeout.')
    },
    {
        label: 'VirtualExecutor',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Java Concurrency) • Lightweight Concurrent Thread Pool',
        insertText: new vscode.SnippetString('VirtualExecutor(max_workers=${1:32})'),
        documentation: new vscode.MarkdownString('**Java Concurrency: `VirtualExecutor`**\n\nHigh-throughput lightweight execution pool for asynchronous microservice tasks.')
    },

    // --- Haven Backend Framework Types ---
    {
        label: 'HavenApp',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend) • Enterprise Microservice Application',
        insertText: new vscode.SnippetString('HavenApp(name="${1:MyService}", port=${2:8080}, cors=True, continuity_audit=True)'),
        documentation: new vscode.MarkdownString('**Haven Backend: `HavenApp`**\n\nEnterprise microservice application container with routing, CORS, rate-limiting, and ODCS audit middleware.')
    },
    {
        label: 'HavenServer',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend) • Concurrent Multi-Threaded HTTP Server',
        insertText: new vscode.SnippetString('HavenServer(host="${1:127.0.0.1}", port=${2:8080})'),
        documentation: new vscode.MarkdownString('**Haven Backend: `HavenServer`**\n\nHigh-performance concurrent multi-threaded HTTP server.')
    },
    {
        label: 'Router',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend) • Declarative HTTP Router',
        insertText: new vscode.SnippetString('Router()'),
        documentation: new vscode.MarkdownString('**Haven Backend: `Router`**\n\nDeclarative HTTP router supporting `@router.get`, `@router.post`, and `{param}` path templates.')
    },
    {
        label: 'Request',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend) • Incoming HTTP Request Object',
        documentation: new vscode.MarkdownString('**Haven Backend: `Request`**\n\nIncoming HTTP request containing method, path, headers, query params, and body bytes.')
    },
    {
        label: 'Response',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend) • Outgoing HTTP Response Object',
        documentation: new vscode.MarkdownString('**Haven Backend: `Response`**\n\nOutgoing HTTP response with status codes, headers, and body payload.')
    },
    {
        label: 'CORSMiddleware',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend) • Cross-Origin Resource Sharing Middleware',
        documentation: new vscode.MarkdownString('**Haven Backend: `CORSMiddleware`**\n\nHandles preflight OPTIONS and cross-origin security headers.')
    },
    {
        label: 'ContinuityAuditMiddleware',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend) • ODCS Transaction Audit Middleware',
        documentation: new vscode.MarkdownString('**Haven Backend: `ContinuityAuditMiddleware`**\n\nCryptographically seals every inbound transaction into the append-only ledger.')
    },
    {
        label: 'RateLimiterMiddleware',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend) • Sliding-Window Rate Limiter',
        documentation: new vscode.MarkdownString('**Haven Backend: `RateLimiterMiddleware`**\n\nProtects API endpoints with sliding-window rate limiting.')
    },
    {
        label: 'DurableModel',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend ORM) • Active-Record ODCS Entity Backed by Merkle Ledger',
        insertText: new vscode.SnippetString('class ${1:ModelName}(DurableModel):\n    id: str = Field(primary_key=True)\n    ${2:name}: str\n    ${3:balance}: Money = Money("0.00", USD)'),
        documentation: new vscode.MarkdownString('**Haven Backend ORM: `DurableModel`**\n\nActive-Record entity backed by the Open Digital Continuity Standard (ODCS). Every mutation is cryptographically sealed into an append-only Merkle ledger, enabling zero-loss disaster recovery and audit replay.\n\n*Methods:* `.create()`, `.find()`, `.filter()`, `.all()`, `.count()`, `.update()`, `.delete()`, `.replay_from_ledger()`.')
    },
    {
        label: 'Field',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend ORM) • Entity Schema Field Descriptor',
        insertText: new vscode.SnippetString('Field(primary_key=${1:False})'),
        documentation: new vscode.MarkdownString('**Haven Backend ORM: `Field`**\n\nSchema field descriptor defining primary key, uniqueness, default values, and nullable constraints.')
    },
    {
        label: 'TestClient',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend Testing) • Zero-Port In-Memory Request Dispatcher',
        documentation: new vscode.MarkdownString('**Haven Backend: `TestClient`**\n\nDirect, zero-port in-memory test runner dispatching simulated requests directly into the router with full cookie, header, and JSON verification.')
    },
    {
        label: 'APIKeyAuthMiddleware',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend Security) • API Key Guard Middleware',
        documentation: new vscode.MarkdownString('**Haven Backend: `APIKeyAuthMiddleware`**\n\nValidates incoming requests against secret API keys via `X-API-Key` header or query param.')
    },
    {
        label: 'BearerAuthMiddleware',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend Security) • Bearer Token Guard Middleware',
        documentation: new vscode.MarkdownString('**Haven Backend: `BearerAuthMiddleware`**\n\nValidates incoming HTTP Bearer tokens via `Authorization: Bearer <token>`.')
    },
    {
        label: 'BackgroundTaskPool',
        kind: vscode.CompletionItemKind.Class,
        detail: 'type (Backend Async) • Background Worker Task Queue',
        documentation: new vscode.MarkdownString('**Haven Backend: `BackgroundTaskPool`**\n\nHigh-throughput worker pool executing asynchronous side-effects, ledger syncs, and telemetry broadcasts.')
    }
];

/**
 * Autocompletion Catalog for Keywords, Annotations and Snippets
 */
const HAVEN_KEYWORD_ITEMS = [
    // Star Language Ergonomics
    { label: 'use', detail: 'use <module> (Star import)', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('use ${1:module}') },
    { label: 'variable', detail: 'variable <name> = <val> (Star declaration)', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('variable ${1:name} = ${2:value}') },
    { label: 'constant', detail: 'constant <NAME> = <val> (Star constant)', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('constant ${1:NAME} = ${2:value}') },
    { label: 'end', detail: 'end (Star block terminator)', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('end') },
    { label: '@require_auth', detail: '@require_auth (Security guard)', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@require_auth') },
    { label: 'mount_ofcs_vault', detail: 'mount_ofcs_vault(app, ledger=None)', kind: vscode.CompletionItemKind.Function, insertText: new vscode.SnippetString('mount_ofcs_vault(${1:app}, ${2:vault_ledger})') },
    // Keywords & English Statements
    { label: 'set', detail: 'set <variable> to <value>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('set ${1:variable} to ${2:value}') },
    { label: 'let', detail: 'let <variable> be <value>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('let ${1:variable} be ${2:value}') },
    { label: 'remember', detail: 'remember <CONSTANT> as <value>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('remember ${1:CONSTANT} as ${2:value}') },
    { label: 'increase', detail: 'increase <variable> by <delta>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('increase ${1:variable} by ${2:1}') },
    { label: 'decrease', detail: 'decrease <variable> by <delta>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('decrease ${1:variable} by ${2:1}') },
    { label: 'whenever', detail: 'whenever <condition>:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('whenever ${1:condition}:\n    ${2:pass}') },
    { label: 'otherwise if', detail: 'otherwise if <condition>:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('otherwise if ${1:condition}:\n    ${2:pass}') },
    { label: 'otherwise', detail: 'otherwise:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('otherwise:\n    ${1:pass}') },
    { label: 'unless', detail: 'unless <condition>:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('unless ${1:condition}:\n    ${2:pass}') },
    { label: 'until', detail: 'until <condition>:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('until ${1:condition}:\n    ${2:pass}') },
    { label: 'repeat', detail: 'repeat <N> times:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('repeat ${1:5} times:\n    ${2:pass}') },
    { label: 'for each', detail: 'for each <item> in <collection>:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('for each ${1:item} in ${2:collection}:\n    ${3:pass}') },
    { label: 'forever', detail: 'forever:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('forever:\n    ${1:pass}') },
    { label: 'give back', detail: 'give back <expression>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('give back ${1:expression}') },
    { label: 'recover', detail: 'recover as <err>:', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('recover as ${1:err}:\n    ${2:pass}') },
    { label: 'ensure', detail: 'ensure <condition> otherwise "<msg>"', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('ensure ${1:condition} otherwise "${2:Error message}"') },
    { label: 'say', detail: 'say <expression>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('say ${1:expression}') },
    { label: 'show', detail: 'show <expression>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('show ${1:expression}') },
    { label: 'checkpoint', detail: 'checkpoint <asset> as "<alias>" into <ledger>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('checkpoint ${1:asset} as "${2:alias}" into ${3:ledger}') },
    { label: 'preserve', detail: 'preserve <payload> as "<alias>" into <ledger>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('preserve ${1:payload} as "${2:alias}" into ${3:ledger}') },
    { label: 'verify', detail: 'verify <asset> with <proof>', kind: vscode.CompletionItemKind.Keyword, insertText: new vscode.SnippetString('verify ${1:asset} with ${2:proof}') },
    { label: 'durable record', detail: 'durable record <Name>:', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('durable record ${1:AssetRecord}:\n    ${2:id}: str\n    ${3:value}: Money') },
    { label: 'define', detail: 'define function_name(param: Type) -> ReturnType:', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('define ${1:name}(${2:param}: ${3:str}) -> ${4:bool}:\n    ${5:give back true}') },

    // Builtin Currencies
    { label: 'USD', detail: 'Currency: US Dollar ($)', kind: vscode.CompletionItemKind.Constant },
    { label: 'EUR', detail: 'Currency: Euro (€)', kind: vscode.CompletionItemKind.Constant },
    { label: 'GBP', detail: 'Currency: British Pound (£)', kind: vscode.CompletionItemKind.Constant },
    { label: 'INR', detail: 'Currency: Indian Rupee (₹)', kind: vscode.CompletionItemKind.Constant },
    { label: 'JPY', detail: 'Currency: Japanese Yen (¥)', kind: vscode.CompletionItemKind.Constant },
    { label: 'BTC', detail: 'Currency: Bitcoin (₿)', kind: vscode.CompletionItemKind.Constant },
    { label: 'HVN', detail: 'Currency: Haven Native Coin (◈)', kind: vscode.CompletionItemKind.Constant },

    // Annotations
    { label: '@Transactional', detail: '@Transactional(rollback_on=(Exception,), audit=True)', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Transactional(rollback_on=(Exception,), audit=True)') },
    { label: '@CircuitBreaker', detail: '@CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@CircuitBreaker(failure_threshold=${1:5}, recovery_timeout=${2:30.0})') },
    { label: '@Retry', detail: '@Retry(max_attempts=3, backoff_factor=2.0)', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Retry(max_attempts=${1:3}, backoff_factor=${2:2.0})') },
    { label: '@FinancialTransaction', detail: '@FinancialTransaction', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@FinancialTransaction') },
    { label: '@Idempotent', detail: '@Idempotent(key_field="tx_id")', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Idempotent') },
    { label: '@ZeroDrift', detail: '@ZeroDrift', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@ZeroDrift') },
    { label: '@Override', detail: '@Override', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Override') },
    { label: '@Sealed', detail: '@Sealed(permits=(...))', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Sealed(permits=(${1:SubClass}))') },
    { label: '@Audit', detail: '@Audit(action_name="...")', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Audit') },
    { label: '@ContinuityCheck', detail: '@ContinuityCheck', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@ContinuityCheck') },
    { label: '@Synchronized', detail: '@Synchronized', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Synchronized') },
    { label: '@Volatile', detail: '@Volatile', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Volatile') },
    { label: '@interface', detail: '@interface CustomAnnotation:', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@interface\nclass ${1:MyAnnotation}:\n    ${2:pass}') },
    { label: '@Retention', detail: '@Retention(policy=RetentionPolicy.RUNTIME)', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Retention(policy=RetentionPolicy.RUNTIME)') },
    { label: '@Target', detail: '@Target(targets=(ElementType.METHOD,))', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Target(targets=(ElementType.METHOD,))') },
    { label: '@Deprecated', detail: '@Deprecated(since="2.0.0")', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Deprecated(since="${1:2.0.0}")') }
];

/**
 * 59 Complete Signatures Catalog for SignatureHelpProvider
 */
const HAVEN_SIGNATURES = {
    // ODCS Durability & Merkle
    'checkpoint': {
        label: 'checkpoint(asset: Any, alias: Optional[str] = None, ledger: Optional[ContinuityLedger] = None) -> LedgerEntry',
        doc: 'ODCS Invariant: Cryptographically seals an asset into the append-only Merkle ledger.'
    },
    'durable_record': {
        label: '@durable_record\nclass RecordName:\n',
        doc: 'ODCS Invariant: Generates immutable state record with deterministic RFC 8785 hashing.'
    },
    'verify_continuity': {
        label: 'verify_continuity(record: Any, proof: Optional[dict] = None) -> bool',
        doc: 'ODCS Invariant: Verifies cryptographic hash and ledger integrity of the record.'
    },
    'ContinuityLedger': {
        label: 'ContinuityLedger(name: str = "primary", storage_path: Optional[str] = None) -> ContinuityLedger',
        doc: 'ODCS Append-only cryptographic ledger with Merkle DAG integrity verification.'
    },
    'LedgerEntry': {
        label: 'LedgerEntry(index: int, timestamp: float, previous_hash: str, entry_hash: str, payload: dict) -> LedgerEntry',
        doc: 'Immutable single block entry in an ODCS ledger.'
    },
    'MerkleTree': {
        label: 'MerkleTree(leaves: Optional[List[str]] = None) -> MerkleTree',
        doc: 'Cryptographic binary Merkle Tree for tamper-evident data proofs.'
    },
    'VectorClock': {
        label: 'VectorClock(node_id: Optional[str] = None) -> VectorClock',
        doc: 'Distributed causality tracker for partial ordering across nodes.'
    },
    'PNCounter': {
        label: 'PNCounter(node_id: str) -> PNCounter',
        doc: 'Conflict-Free Replicated Data Type (CRDT) positive-negative counter.'
    },
    'AWORSet': {
        label: 'AWORSet(node_id: str) -> AWORSet',
        doc: 'Add-Wins Observed-Removed Set CRDT collection.'
    },
    'LWWRegister': {
        label: 'LWWRegister(node_id: str) -> LWWRegister',
        doc: 'Last-Write-Wins Register CRDT with timestamp ordering.'
    },
    'OutboxPipeline': {
        label: 'OutboxPipeline(node_id: str) -> OutboxPipeline',
        doc: 'Store-and-forward outbox queue with monotonic deduplication.'
    },
    'MeshNode': {
        label: 'MeshNode(node_id: str, host: str, port: int) -> MeshNode',
        doc: 'P2P Mesh participant node in the gossip network.'
    },
    'GossipMesh': {
        label: 'GossipMesh(local_node: MeshNode) -> GossipMesh',
        doc: 'Decentralized peer-to-peer epidemic dissemination mesh.'
    },
    'EnvironmentalTelemetry': {
        label: 'EnvironmentalTelemetry() -> EnvironmentalTelemetry',
        doc: 'Probes connectivity mode, latency, and power budget.'
    },
    'ZeroIntentLossManager': {
        label: 'ZeroIntentLossManager() -> ZeroIntentLossManager',
        doc: 'ODCS Layer 4 Invariant: Guarantees zero lost user operations during network failure.'
    },
    'ContinuityAlgorithm': {
        label: 'ContinuityAlgorithm(name: str) -> ContinuityAlgorithm',
        doc: 'Base class for deterministic state machines with journal replay guarantees.'
    },
    'ODCSApp': {
        label: 'ODCSApp(name: str = "ODCSApplication") -> ODCSApp',
        doc: 'Enterprise ODCS application container with continuity gateway.'
    },

    // OFCS Financial
    'Money': {
        label: 'Money(amount: Union[str, int, float, Decimal], currency: Currency = USD) -> Money',
        doc: 'OFCS Invariant: Zero-drift decimal currency representation with exact monetary arithmetic.'
    },
    'Currency': {
        label: 'Currency(code: str, symbol: str, precision: int = 2) -> Currency',
        doc: 'OFCS Invariant: ISO-4217 financial currency descriptor.'
    },
    'ExchangeRate': {
        label: 'ExchangeRate(source: Currency, target: Currency, rate: Union[str, Decimal]) -> ExchangeRate',
        doc: 'OFCS Invariant: Deterministic cross-currency atomic exchange rate multiplier.'
    },
    'DoubleEntryRecord': {
        label: 'DoubleEntryRecord(tx_id: str, debits: List[Money], credits: List[Money], description: str = "") -> DoubleEntryRecord',
        doc: 'OFCS Invariant 1: sum(debits) == sum(credits). Prevents unbalanced entries.'
    },
    'FinancialAccount': {
        label: 'FinancialAccount(account_id: str, currency: Currency = USD, allow_overdraft: bool = False) -> FinancialAccount',
        doc: 'OFCS Invariant: Double-entry ledger balance account with audit trail.'
    },
    'OFCSFinancialLedger': {
        label: 'OFCSFinancialLedger(ledger_name: str = "ofcs_primary", storage_path: Optional[str] = None) -> OFCSFinancialLedger',
        doc: 'OFCS Invariant: Tamper-evident financial double-entry ledger with WAL commit log.'
    },
    'ReconciliationEngine': {
        label: 'ReconciliationEngine(primary_ledger: OFCSFinancialLedger) -> ReconciliationEngine',
        doc: 'Performs branch reconciliation and zero-loss convergence for offline financial ledgers.'
    },

    // Annotations
    'interface': {
        label: '@interface\nclass CustomAnnotation:',
        doc: 'Defines a custom Java-style metadata annotation.'
    },
    'Retention': {
        label: '@Retention(policy: RetentionPolicy = RetentionPolicy.RUNTIME)',
        doc: 'Specifies annotation availability at RUNTIME, CLASS, or SOURCE.'
    },
    'Target': {
        label: '@Target(targets: Tuple[ElementType, ...])',
        doc: 'Restricts annotation application to TYPE, METHOD, FIELD, or PARAMETER.'
    },
    'Override': {
        label: '@Override',
        doc: 'Enforces that the annotated method overrides a superclass or interface method.'
    },
    'Deprecated': {
        label: '@Deprecated(since: str = "", for_removal: bool = False)',
        doc: 'Marks an API element as deprecated.'
    },
    'Synchronized': {
        label: '@Synchronized(lock: Optional[threading.Lock] = None)',
        doc: 'Acquires reentrant mutex lock before executing method.'
    },
    'Volatile': {
        label: '@Volatile',
        doc: 'Ensures variable memory visibility across threads.'
    },
    'Sealed': {
        label: '@Sealed(permits: Tuple[Type, ...])',
        doc: 'Java 17 style sealed hierarchy restricting permitted subclasses.'
    },
    'Durable': {
        label: '@Durable',
        doc: 'Enforces state preservation into ODCS append-only ledger.'
    },
    'Transactional': {
        label: '@Transactional(rollback_on: Tuple[Type[Exception], ...] = (Exception,), audit: bool = True)',
        doc: 'ODCS Transactional Boundary: Checks in receipt on success, records rollback entry on failure.'
    },
    'Audit': {
        label: '@Audit(action_name: Optional[str] = None, ledger: Optional[ContinuityLedger] = None)',
        doc: 'ODCS Invariant: Logs function invocation, parameters, and return value to the ledger.'
    },
    'ContinuityCheck': {
        label: '@ContinuityCheck',
        doc: 'Verifies system continuity invariants before and after invocation.'
    },
    'CircuitBreaker': {
        label: '@CircuitBreaker(failure_threshold: int = 5, recovery_timeout: float = 30.0, fallback: Optional[Callable] = None)',
        doc: 'Enterprise fault tolerance circuit breaker preventing cascading outages.'
    },
    'Retry': {
        label: '@Retry(max_attempts: int = 3, backoff_factor: float = 2.0, exceptions: Tuple[Type[Exception], ...] = (Exception,))',
        doc: 'Enterprise exponential backoff retry policy.'
    },
    'FinancialTransaction': {
        label: '@FinancialTransaction(idempotency_key: Optional[str] = None, ledger: Optional[OFCSFinancialLedger] = None)',
        doc: 'OFCS Invariant: Wraps financial flow in double-entry atomicity.'
    },
    'Idempotent': {
        label: '@Idempotent(key_field: str = "tx_id")',
        doc: 'Prevents duplicate execution of identical operations.'
    },
    'ZeroDrift': {
        label: '@ZeroDrift(allowed_tolerance: Decimal = Decimal("0"))',
        doc: 'OFCS Invariant: Asserts zero floating-point loss across all calculated output.'
    },

    // Java Concurrency
    'CompletableFuture': {
        label: 'CompletableFuture[T]() -> CompletableFuture[T]',
        doc: 'Asynchronous promise-like computation model for non-blocking reactive concurrency.'
    },
    'CompletableFuture.supply_async': {
        label: 'CompletableFuture.supply_async(supplier: Callable[[], T], executor: Optional[VirtualExecutor] = None) -> CompletableFuture[T]',
        doc: 'Executes supplier asynchronously on a virtual worker thread.'
    },
    'CompletableFuture.run_async': {
        label: 'CompletableFuture.run_async(runnable: Callable[[], None], executor: Optional[VirtualExecutor] = None) -> CompletableFuture[None]',
        doc: 'Executes runnable asynchronously without return value.'
    },
    'AtomicInteger': {
        label: 'AtomicInteger(initial_value: int = 0) -> AtomicInteger',
        doc: 'Lock-free atomic integer supporting compare_and_set, increment, and decrement.'
    },
    'AtomicBoolean': {
        label: 'AtomicBoolean(initial_value: bool = False) -> AtomicBoolean',
        doc: 'Lock-free atomic boolean supporting atomic toggle and CAS.'
    },
    'AtomicReference': {
        label: 'AtomicReference(initial_value: Any = None) -> AtomicReference[T]',
        doc: 'Lock-free atomic object reference with compare_and_set.'
    },
    'CountDownLatch': {
        label: 'CountDownLatch(count: int) -> CountDownLatch',
        doc: 'Synchronization barrier blocking threads until count reaches zero.'
    },
    'ReentrantLock': {
        label: 'ReentrantLock() -> ReentrantLock',
        doc: 'Reentrant mutual exclusion lock supporting try_lock with timeout.'
    },
    'VirtualExecutor': {
        label: 'VirtualExecutor(max_workers: int = 32) -> VirtualExecutor',
        doc: 'Lightweight concurrent execution thread pool.'
    },

    // Backend
    'HavenApp': {
        label: 'HavenApp(name: str = "HavenApplication", host: str = "127.0.0.1", port: int = 8080, cors: bool = True, continuity_audit: bool = True, rate_limit: int = 1200) -> HavenApp',
        doc: 'Enterprise Haven Microservice Application Container with built-in ODCS REST endpoints.'
    },
    'HavenServer': {
        label: 'HavenServer(host: str = "127.0.0.1", port: int = 8080, router: Optional[Router] = None, verbose: bool = False) -> HavenServer',
        doc: 'High-Performance Concurrent Multi-Threaded HTTP Server.'
    },
    'Router': {
        label: 'Router() -> Router',
        doc: 'Declarative HTTP router supporting @router.get, @router.post, and {param} path templates.'
    },
    'Request': {
        label: 'Request(method: str, path: str, headers: Optional[dict] = None, query_params: Optional[dict] = None, body_bytes: bytes = b"") -> Request',
        doc: 'Incoming HTTP request object in Haven backend.'
    },
    'Response': {
        label: 'Response(status_code: int = 200, headers: Optional[dict] = None, body_bytes: bytes = b"") -> Response',
        doc: 'Outgoing HTTP response object.'
    },
    'Response.json': {
        label: 'Response.json(data: Any, status_code: int = 200, headers: Optional[dict] = None) -> Response',
        doc: 'Mints JSON response with automatic ODCS/OFCS type serialization.'
    },
    'Response.ok': {
        label: 'Response.ok(message: str = "OK", data: Any = None) -> Response',
        doc: 'Mints standard 200 OK response.'
    },
    'Response.error': {
        label: 'Response.error(message: str, status_code: int = 400, error_code: str = "ERROR") -> Response',
        doc: 'Mints structured JSON error response.'
    },
    'Response.text': {
        label: 'Response.text(content: str, status_code: int = 200, content_type: str = "text/plain; charset=utf-8") -> Response',
        doc: 'Mints raw text response.'
    },
    'CORSMiddleware': {
        label: 'CORSMiddleware(allow_origins: str = "*", allow_methods: str = "GET, POST, PUT, DELETE, OPTIONS, PATCH") -> CORSMiddleware',
        doc: 'Cross-Origin Resource Sharing middleware.'
    },
    'ContinuityAuditMiddleware': {
        label: 'ContinuityAuditMiddleware(ledger: Optional[ContinuityLedger] = None) -> ContinuityAuditMiddleware',
        doc: 'ODCS Invariant: Seals every incoming transaction into the Merkle ledger.'
    },
    'RateLimiterMiddleware': {
        label: 'RateLimiterMiddleware(max_requests_per_minute: int = 600) -> RateLimiterMiddleware',
        doc: 'Sliding-window rate limiter protecting API endpoints.'
    },
    'DurableModel': {
        label: 'class DurableModel(metaclass=DurableModelMeta)',
        doc: 'Active-Record ODCS Entity backed by Merkle append-only ledger.'
    },
    'DurableModel.create': {
        label: 'DurableModel.create(**kwargs) -> DurableModel',
        doc: 'Instantiates entity and seals an append-only commit entry in the ledger.'
    },
    'DurableModel.find': {
        label: 'DurableModel.find(pk: Any) -> Optional[DurableModel]',
        doc: 'Finds an entity by primary key in O(1) time.'
    },
    'DurableModel.filter': {
        label: 'DurableModel.filter(predicate: Optional[Callable] = None, **kwargs) -> List[DurableModel]',
        doc: 'Filters stored entities matching criteria or custom predicate.'
    },
    'DurableModel.replay_from_ledger': {
        label: 'DurableModel.replay_from_ledger(ledger: Optional[ContinuityLedger] = None) -> int',
        doc: 'Deterministic disaster recovery: reconstructs entity table from cryptographic Merkle ledger.'
    },
    'Field': {
        label: 'Field(default: Any = None, primary_key: bool = False, nullable: bool = False, unique: bool = False)',
        doc: 'Descriptor defining schema constraints for a DurableModel column.'
    },
    'TestClient': {
        label: 'TestClient(app: HavenApp) -> TestClient',
        doc: 'In-memory zero-port testing client for Haven backend applications.'
    },
    'APIKeyAuthMiddleware': {
        label: 'APIKeyAuthMiddleware(api_key: str, header_name: str = "X-API-Key")',
        doc: 'Secures backend endpoints with cryptographic API key verification.'
    },
    'BearerAuthMiddleware': {
        label: 'BearerAuthMiddleware(token: str)',
        doc: 'Secures backend endpoints with HTTP Bearer token verification.'
    },
    'BackgroundTaskPool': {
        label: 'BackgroundTaskPool(max_workers: int = 8)',
        doc: 'High-throughput asynchronous background job worker pool.'
    },
    'mount_ofcs_vault': {
        label: 'mount_ofcs_vault(app: HavenApp, ledger: Optional[OFCSFinancialLedger] = None) -> OFCSFinancialLedger',
        doc: 'Mounts turnkey OFCS double-entry banking vault endpoints into HavenApp.'
    }
};

/**
 * Hover Documentation Catalog
 */
const HAVEN_HOVER_DOCS = {
    // Star Language Keywords
    'use': '**Star Language Ergonomics: `use <module>`**\n\nImports a module or package into the local namespace, identical to `import <module>`.\n\n*Example:*\n```haven\nuse haven\nuse ofcs\n```',
    'variable': '**Star Language Ergonomics: `variable <name> = <value>`**\n\nDeclares a mutable state variable, identical to `set <name> to <value>`.\n\n*Example:*\n```haven\nvariable active_nodes = 5\nincrease active_nodes by 2\n```',
    'constant': '**Star Language Ergonomics: `constant <NAME> = <value>`**\n\nDeclares a compile-time immutable constant, identical to `remember <NAME> as <value>`.\n\n*Example:*\n```haven\nconstant TIMEOUT_MS = 5000\n```',
    'end': '**Star Language Ergonomics: `end`**\n\nExplicit block terminator for functions, conditionals, and loops.\n\n*Example:*\n```haven\nfunction compute(x):\n    whenever x > 0:\n        give back x * 2\n    end\nend\n```',
    'require_auth': '**Haven Backend: `@require_auth`**\n\nRoute decorator enforcing API Key or Bearer token authentication before handler dispatch.\n\n*Example:*\n```haven\n@app.get("/secret")\n@require_auth\ndef get_secret(req: Request) -> Response:\n    give back Response.ok("Granted")\n```',
    'mount_ofcs_vault': '**Haven Backend: `mount_ofcs_vault(app, ledger=None)`**\n\nMounts turnkey enterprise banking endpoints (`/vault/accounts`, `/vault/transfers`, `/vault/audit`) enforcing OFCS Invariant 1 (Debits == Credits).\n\n*Example:*\n```haven\napp.mount_vault(vault_ledger)\n```',
    'DurableModel': '**Haven Backend ORM: `DurableModel`**\n\nActive-Record entity backed by the Open Digital Continuity Standard (ODCS). Mutations are cryptographically sealed into an append-only Merkle ledger for 100% deterministic disaster recovery.\n\n*Example:*\n```haven\nclass Customer(DurableModel):\n    id: str = Field(primary_key=True)\n    name: str\n    balance: Money\n```',
    'Field': '**Haven Backend ORM: `Field`**\n\nField schema descriptor for `DurableModel` entities.\n\n*Example:*\n```haven\nid: str = Field(primary_key=True)\n```',
    'TestClient': '**Haven Backend: `TestClient`**\n\nDirect, zero-port in-memory test runner for Haven backend applications.\n\n*Example:*\n```haven\nlet client be app.test_client()\nlet res be client.get("/api/v1/ping")\nensure res.status_code == 200 otherwise "Ping failed"\n```',
    // English Keywords
    'set': '**Haven Language Keyword: `set ... to`**\n\nSets or mutates state in natural English.\n\n*Example:*\n```haven\nset active_connections: int to 42\n```',
    'let': '**Haven Language Keyword: `let ... be`**\n\nBinds local variables.\n\n*Example:*\n```haven\nlet rate: float be 0.05\n```',
    'remember': '**Haven Language Keyword: `remember ... as`**\n\nDeclares an immutable constant bound to the namespace.\n\n*Example:*\n```haven\nremember STANDARD as "ODCS-1.0.0"\n```',
    'increase': '**Haven Language Keyword: `increase ... by`**\n\nIncrements numeric state by specified delta.\n\n*Example:*\n```haven\nincrease attempts by 1\n```',
    'decrease': '**Haven Language Keyword: `decrease ... by`**\n\nDecrements numeric state by specified delta.\n\n*Example:*\n```haven\ndecrease balance by 50\n```',
    'whenever': '**Haven Language Keyword: `whenever`**\n\nConditional branching in natural English.\n\n*Example:*\n```haven\nwhenever count > 10:\n    say "Threshold reached"\notherwise if count == 10:\n    say "Exact threshold"\notherwise:\n    say "Below threshold"\n```',
    'otherwise': '**Haven Language Keyword: `otherwise`**\n\nFallback branch for conditional statements.',
    'unless': '**Haven Language Keyword: `unless`**\n\nInverted conditional block; executes when condition is false.\n\n*Example:*\n```haven\nunless is_connected:\n    reconnect()\n```',
    'until': '**Haven Language Keyword: `until`**\n\nNatural loop repeating while condition remains false.\n\n*Example:*\n```haven\nuntil queue.is_empty():\n    process_item(queue.pop())\n```',
    'repeat': '**Haven Language Keyword: `repeat ... times`**\n\nHigh-performance loop executed exactly N times.\n\n*Example:*\n```haven\nrepeat 5 times:\n    ping_host()\n```',
    'forever': '**Haven Language Keyword: `forever:`**\n\nSub-millisecond infinite event loop.\n\n*Example:*\n```haven\nforever:\n    poll_events()\n```',
    'give': '**Haven Language Keyword: `give back`**\n\nReturns a value from a function or subroutine.\n\n*Example:*\n```haven\ngive back total_latency\n```',
    'recover': '**Haven Language Keyword: `recover as <err>:`**\n\nNatural exception handling block.\n\n*Example:*\n```haven\ntry:\n    commit_block()\nrecover as err:\n    say "Handled error:", err\nalways:\n    close_socket()\n```',
    'ensure': '**Haven Language Keyword: `ensure ... otherwise`**\n\nEvaluates invariant assertion with custom failure message.\n\n*Example:*\n```haven\nensure balance >= 0 otherwise "Negative balance violation"\n```',
    'say': '**Haven Language Keyword: `say`**\n\nPrints formatted output to standard console.\n\n*Example:*\n```haven\nsay "Server running on port {port}"\n```',
    'show': '**Haven Language Keyword: `show`**\n\nPrints expressions and inspection objects directly.\n\n*Example:*\n```haven\nshow ledger.head_hash\n```',
    'durable': '**ODCS Layer 1: `durable record`**\n\nDefines a schema-enforced, immutable record type for local Write-Ahead Logging (WAL) and Zero Intent Loss.\n\n*Example:*\n```haven\ndurable record TriageVital:\n    patient_id: str\n    heart_rate: int\n```',
    'checkpoint': '**ODCS Layer 1: `checkpoint`**\n\nAtomically writes a durable record into an append-only cryptographic ledger with Merkle DAG validation.\n\n*Example:*\n```haven\ncheckpoint vital as "triage_read" into primary_ledger\n```',
    'preserve': '**ODCS Invariant: `preserve`**\n\nSeals operation intent into append-only local storage.\n\n*Example:*\n```haven\npreserve action as "user_click" into ledger\n```',
    'verify': '**ODCS Invariant: `verify`**\n\nValidates cryptographic SHA-256 Merkle proofs against root hash.\n\n*Example:*\n```haven\nverify asset with proof\n```',

    // Types
    'str': '**Haven Primitive Type: `str`**\n\nImmutable UTF-8 String Sequence.',
    'int': '**Haven Primitive Type: `int`**\n\n64-bit Arbitrary-Precision Integer.',
    'float': '**Haven Primitive Type: `float`**\n\nIEEE 754 Double-Precision Float.',
    'bool': '**Haven Primitive Type: `bool`**\n\nBoolean Flag (`true` or `false`).',
    'bytes': '**Haven Primitive Type: `bytes`**\n\nImmutable Byte Buffer for binary payloads and hashes.',
    'list': '**Haven Primitive Type: `list`**\n\nDynamic ordered sequence.',
    'dict': '**Haven Primitive Type: `dict`**\n\nKey-value associative hash map.',
    'Decimal': '**Haven Type: `Decimal`**\n\nExact fixed-point decimal arithmetic.',
    'Optional': '**Type Hint: `Optional[T]`**\n\nIndicates a type can be `T` or `None` (`nothing`).',
    'Union': '**Type Hint: `Union[T1, T2]`**\n\nMatches either `T1` or `T2`.',
    'List': '**Type Hint: `List[T]`**\n\nHomogeneous list of elements of type `T`.',
    'Dict': '**Type Hint: `Dict[K, V]`**\n\nTyped dictionary with keys of type `K` and values of type `V`.',
    'Money': '**OFCS Invariant: `Money`**\n\nZero-drift high-precision decimal monetary value with strict currency safety.\n\n*Example:*\n```haven\nset amount: Money to Money("150.00", USD)\n```',
    'DoubleEntryRecord': '**OFCS Invariant 1: `DoubleEntryRecord`**\n\nEnforces mathematical double-entry balance: `sum(debits) == sum(credits)`.\n\n*Example:*\n```haven\nset tx: DoubleEntryRecord to DoubleEntryRecord("TX-101", debits=[m1], credits=[m2])\n```',
    'FinancialAccount': '**OFCS Invariant: `FinancialAccount`**\n\nAudited double-entry ledger account with balance tracking.',
    'OFCSFinancialLedger': '**OFCS Invariant: `OFCSFinancialLedger`**\n\nTamper-evident double-entry financial ledger with cryptographic receipt tracking.',
    'ContinuityLedger': '**ODCS Type: `ContinuityLedger`**\n\nLocal append-only WAL & Merkle DAG root calculation.',
    'LedgerEntry': '**ODCS Type: `LedgerEntry`**\n\nImmutable single block entry in an ODCS ledger.',
    'MerkleTree': '**ODCS Type: `MerkleTree`**\n\nCryptographic binary Merkle Tree for tamper-evident proofs.',
    'VectorClock': '**ODCS Type: `VectorClock`**\n\nDistributed causality tracker across nodes.',
    'PNCounter': '**ODCS Type: `PNCounter`**\n\nConflict-Free Replicated Data Type (CRDT) positive-negative counter.',
    'AWORSet': '**ODCS Type: `AWORSet`**\n\nAdd-Wins Observed-Removed Set CRDT collection.',
    'CompletableFuture': '**Java Concurrency: `CompletableFuture`**\n\nNon-blocking reactive promise pipeline for asynchronous task composition.',
    'AtomicInteger': '**Java Concurrency: `AtomicInteger`**\n\nLock-free atomic integer supporting compare_and_set, increment, decrement.',
    'AtomicBoolean': '**Java Concurrency: `AtomicBoolean`**\n\nLock-free atomic boolean supporting atomic toggle and CAS.',
    'HavenApp': '**Haven Backend: `HavenApp`**\n\nEnterprise microservice application container with routing, CORS, rate-limiting, and ODCS audit middleware.',
    'HavenServer': '**Haven Backend: `HavenServer`**\n\nConcurrent multi-threaded HTTP server with REST routing and ODCS continuity verification.',
    'Router': '**Haven Backend: `Router`**\n\nDeclarative HTTP router supporting path parameters and method decorators.',
    'Request': '**Haven Backend: `Request`**\n\nIncoming HTTP request object.',
    'Response': '**Haven Backend: `Response`**\n\nOutgoing HTTP response object with JSON and status minting.',

    // Annotations
    'Transactional': '**Enterprise Annotation: `@Transactional`**\n\nEnforces atomic ledger commits on success, and mints rollback receipts on exceptions.',
    'CircuitBreaker': '**Enterprise Annotation: `@CircuitBreaker`**\n\nFault-tolerance circuit breaker preventing cascading outages across microservices.',
    'Retry': '**Enterprise Annotation: `@Retry`**\n\nResilience decorator implementing exponential backoff retries.',
    'FinancialTransaction': '**OFCS Annotation: `@FinancialTransaction`**\n\nEnforces double-entry financial atomicity.',
    'Idempotent': '**OFCS Annotation: `@Idempotent`**\n\nGuarantees duplicate requests yield identical result without state re-mutation.',
    'ZeroDrift': '**OFCS Annotation: `@ZeroDrift`**\n\nValidates zero decimal precision loss across computations.',
    'Override': '**Java Contract: `@Override`**\n\nEnforces that method overrides an interface or superclass definition.',
    'Sealed': '**Java 17 Concept: `@Sealed(permits=(...))`**\n\nRestricts inheritance hierarchy strictly to specified subclasses.'
};

/**
 * Extension Activation Entry Point
 */
function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('haven');
    context.subscriptions.push(diagnosticCollection);

    // Register Hover Provider
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(HAVEN_SELECTOR, {
            provideHover(document, position) {
                const wordRange = document.getWordRangeAtPosition(position, /[\w-]+/);
                if (!wordRange) return null;
                const word = document.getText(wordRange);

                if (HAVEN_HOVER_DOCS[word]) {
                    return new vscode.Hover(new vscode.MarkdownString(HAVEN_HOVER_DOCS[word]));
                }

                // Check in signatures
                if (HAVEN_SIGNATURES[word]) {
                    const sig = HAVEN_SIGNATURES[word];
                    return new vscode.Hover(new vscode.MarkdownString(`\`\`\`haven\n${sig.label}\n\`\`\`\n\n${sig.doc}`));
                }

                // Check in types catalog
                const foundType = HAVEN_TYPE_ITEMS.find(t => t.label === word);
                if (foundType && foundType.documentation) {
                    return new vscode.Hover(foundType.documentation);
                }

                return null;
            }
        })
    );

    // Register Context-Aware Autocompletion Provider with Type Suggestions
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            HAVEN_SELECTOR,
            {
                provideCompletionItems(document, position, token, context) {
                    const lineText = document.lineAt(position.line).text;
                    const linePrefix = lineText.substring(0, position.character);

                    // Detect Type Annotation Context:
                    // 1. After colon: e.g. "param:", "balance: ", "patient_id:"
                    // 2. After arrow: e.g. "-> " (function return type)
                    // 3. Inside generic brackets: e.g. "List[", "Optional["
                    // 4. Inside a 'durable record' declaration body
                    const isAfterColon = /:\s*[\w]*$/.test(linePrefix);
                    const isAfterArrow = /->\s*[\w]*$/.test(linePrefix);
                    const isInsideGeneric = /\[\s*[\w, ]*$/.test(linePrefix);

                    let isInsideDurableRecord = false;
                    for (let l = position.line - 1; l >= Math.max(0, position.line - 20); l--) {
                        const prevLine = document.lineAt(l).text;
                        if (/^\s*durable\s+record\s+\w+:/i.test(prevLine)) {
                            isInsideDurableRecord = true;
                            break;
                        }
                        if (/^\S/.test(prevLine) && !prevLine.trim().startsWith('#')) {
                            break; // Dedented to root
                        }
                    }

                    const isTypeContext = isAfterColon || isAfterArrow || isInsideGeneric || (isInsideDurableRecord && linePrefix.trim().includes(':'));

                    if (isTypeContext) {
                        // Prioritize Type Suggestions to top of completion list
                        return HAVEN_TYPE_ITEMS.map((typeItem, index) => {
                            const item = new vscode.CompletionItem(typeItem.label, typeItem.kind);
                            item.detail = typeItem.detail;
                            item.documentation = typeItem.documentation;
                            if (typeItem.insertText) {
                                item.insertText = typeItem.insertText;
                            }
                            // Sort types first in type contexts
                            item.sortText = '0_' + String(index).padStart(3, '0') + '_' + typeItem.label;
                            return item;
                        });
                    }

                    // Standard completion context: Offer Keywords, Types, Annotations & Methods
                    const allItems = [];

                    // Add all Type Suggestions
                    for (const typeItem of HAVEN_TYPE_ITEMS) {
                        const item = new vscode.CompletionItem(typeItem.label, typeItem.kind);
                        item.detail = typeItem.detail;
                        item.documentation = typeItem.documentation;
                        if (typeItem.insertText) {
                            item.insertText = typeItem.insertText;
                        }
                        item.sortText = '1_' + typeItem.label;
                        allItems.push(item);
                    }

                    // Add all Keywords & Snippets
                    for (const kwItem of HAVEN_KEYWORD_ITEMS) {
                        const item = new vscode.CompletionItem(kwItem.label, kwItem.kind);
                        item.detail = kwItem.detail;
                        if (kwItem.insertText) {
                            item.insertText = kwItem.insertText;
                        }
                        item.sortText = '2_' + kwItem.label;
                        allItems.push(item);
                    }

                    return allItems;
                }
            },
            '.', '@', ':', '>', '[', ' '
        )
    );

    // Register Complete 59+ Signature Help Provider
    context.subscriptions.push(
        vscode.languages.registerSignatureHelpProvider(
            HAVEN_SELECTOR,
            {
                provideSignatureHelp(document, position) {
                    const lineText = document.lineAt(position.line).text.substring(0, position.character);

                    // Scan backwards to find matching function or class call
                    for (const [funcName, sigData] of Object.entries(HAVEN_SIGNATURES)) {
                        // Check if line contains funcName( and cursor is after it
                        const pattern = new RegExp(`\\b${funcName.replace('.', '\\.')}\\s*\\(([^)]*)$`);
                        const match = lineText.match(pattern);
                        if (match) {
                            const help = new vscode.SignatureHelp();
                            const sig = new vscode.SignatureInformation(sigData.label, new vscode.MarkdownString(sigData.doc));

                            // Extract parameter strings from the signature label
                            const paramMatch = sigData.label.match(/\((.*?)\)/);
                            if (paramMatch && paramMatch[1].trim()) {
                                const rawParams = paramMatch[1].split(',');
                                sig.parameters = rawParams.map(p => new vscode.ParameterInformation(p.trim()));
                            }

                            // Calculate active parameter based on commas
                            const insideArgs = match[1];
                            let paramIndex = 0;
                            let parenDepth = 0;
                            let bracketDepth = 0;
                            for (let i = 0; i < insideArgs.length; i++) {
                                const ch = insideArgs[i];
                                if (ch === '(') parenDepth++;
                                else if (ch === ')') parenDepth--;
                                else if (ch === '[') bracketDepth++;
                                else if (ch === ']') bracketDepth--;
                                else if (ch === ',' && parenDepth === 0 && bracketDepth === 0) {
                                    paramIndex++;
                                }
                            }

                            help.signatures = [sig];
                            help.activeSignature = 0;
                            help.activeParameter = paramIndex;
                            return help;
                        }
                    }
                    return null;
                }
            },
            '(', ',', ' '
        )
    );

    // Status Bar Item with Fox Mascot Branding
    havenStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    havenStatusBarItem.text = '🦊 Haven Fox';
    havenStatusBarItem.tooltip = 'Haven Programming Language (ODCS Native Edition) • Protected by Haven Fox';
    havenStatusBarItem.command = 'heaven.showMenu';
    context.subscriptions.push(havenStatusBarItem);

    function updateStatusBar() {
        const editor = vscode.window.activeTextEditor;
        if (editor && (editor.document.languageId === 'heaven' || editor.document.languageId === 'haven' ||
            editor.document.fileName.endsWith('.hvn') || editor.document.fileName.endsWith('.haven'))) {
            havenStatusBarItem.show();
        } else {
            havenStatusBarItem.hide();
        }
    }
    vscode.window.onDidChangeActiveTextEditor(updateStatusBar);
    updateStatusBar();

    // Document validation listeners
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(doc => validateDocument(doc)),
        vscode.workspace.onDidOpenTextDocument(doc => validateDocument(doc))
    );
    if (vscode.window.activeTextEditor) {
        validateDocument(vscode.window.activeTextEditor.document);
    }

    // Command: heaven.run
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.run', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active Haven source file to run.');
                return;
            }
            const { havenExe } = getHavenRunnerInfo();
            const filePath = editor.document.fileName;
            runInTerminal('🦊 Haven VM', `"${havenExe}" "${filePath}"`);
        })
    );

    // Command: heaven.test
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.test', () => {
            const { havenExe } = getHavenRunnerInfo();
            runInTerminal('🦊 Haven Test Suite', `"${havenExe}" -m haven.cli test`);
        })
    );

    // Command: heaven.lint
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.lint', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active Haven source file to check.');
                return;
            }
            validateDocument(editor.document);
            vscode.window.showInformationMessage('🦊 Haven Fox: Real-time syntax check complete.');
        })
    );

    // Command: heaven.compile
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.compile', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active Haven source file to compile.');
                return;
            }
            const { havenExe } = getHavenRunnerInfo();
            const filePath = editor.document.fileName;
            runInTerminal('🦊 Haven Compiler', `"${havenExe}" -m haven.cli compile "${filePath}"`);
        })
    );

    // Command: heaven.startServer
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.startServer', () => {
            const { havenExe } = getHavenRunnerInfo();
            runInTerminal('🦊 Haven Microservice', `"${havenExe}" -c "import haven; app = haven.HavenApp(name='HavenService', port=8080); app.run()"`);
        })
    );

    // Command: heaven.repl
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.repl', () => {
            const { havenExe } = getHavenRunnerInfo();
            runInTerminal('🦊 Haven Interactive REPL', `"${havenExe}" -m haven.cli repl`);
        })
    );

    // Command: heaven.showMenu
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.showMenu', async () => {
            const options = [
                { label: '🦊 Run Active Haven File', command: 'heaven.run' },
                { label: '🧪 Run Haven ODCS/OFCS Test Suite', command: 'heaven.test' },
                { label: '🔍 Check File Syntax (Linter)', command: 'heaven.lint' },
                { label: '⚡ Compile Haven to Bytecode', command: 'heaven.compile' },
                { label: '🚀 Launch Haven Microservice Backend Server', command: 'heaven.startServer' },
                { label: '💬 Open Interactive Haven REPL', command: 'heaven.repl' }
            ];

            const selected = await vscode.window.showQuickPick(options, {
                placeHolder: '🦊 Haven Language • Select Action'
            });

            if (selected) {
                vscode.commands.executeCommand(selected.command);
            }
        })
    );
}

function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.dispose();
    }
    if (havenStatusBarItem) {
        havenStatusBarItem.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};
