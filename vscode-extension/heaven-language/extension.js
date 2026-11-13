/**
 * 🕊️ Heaven (Haven) Programming Language Visual Studio Code Extension
 * Provides Syntax Highlighting, Real-Time AST Linting Diagnostics,
 * Natural-English Hover Tooltips, Transpilation to Python IR, and
 * ODCS Digital Continuity Gateway integration.
 * Architect: Anirudha Puthraya · Standard: ODCS-2.0.0
 */

const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');
const fs = require('fs');

let diagnosticCollection;
let heavenStatusBarItem;

/**
 * Locate the haven_lang.py runner and python interpreter.
 */
function getHavenRunnerInfo() {
    const config = vscode.workspace.getConfiguration('heaven');
    const customRunner = config.get('runnerPath');
    if (customRunner && fs.existsSync(customRunner)) {
        return { runner: customRunner, python: 'python' };
    }

    // Search workspace folders for heaven/haven_lang.py
    const workspaceFolders = vscode.workspace.workspaceFolders || [];
    for (const folder of workspaceFolders) {
        const candidate = path.join(folder.uri.fsPath, 'heaven', 'haven_lang.py');
        if (fs.existsSync(candidate)) {
            return { runner: candidate, python: 'python' };
        }
        const rootCandidate = path.join(folder.uri.fsPath, 'haven_lang.py');
        if (fs.existsSync(rootCandidate)) {
            return { runner: rootCandidate, python: 'python' };
        }
    }

    // Default fallback
    return { runner: 'heaven/haven_lang.py', python: 'python' };
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
 * Run syntax diagnostics using haven_lang.py lint.
 */
function validateDocument(document) {
    if (document.languageId !== 'heaven' && !document.fileName.endsWith('.hvn') && !document.fileName.endsWith('.heaven')) {
        return;
    }

    const { runner, python } = getHavenRunnerInfo();
    const filePath = document.fileName;

    cp.exec(`"${python}" "${runner}" lint "${filePath}"`, (err, stdout, stderr) => {
        const diagnostics = [];
        const combined = (stderr || '') + '\n' + (stdout || '');

        // Match "[Haven SyntaxError] line X: message"
        const errMatch = combined.match(/\[Haven SyntaxError\]\s+line\s+(\d+):\s+(.+)/i);
        if (errMatch) {
            const lineNum = Math.max(0, parseInt(errMatch[1], 10) - 1);
            const message = errMatch[2].trim();
            const lineText = document.lineAt(Math.min(lineNum, document.lineCount - 1)).text;
            const startChar = lineText.search(/\S/);
            const range = new vscode.Range(lineNum, Math.max(0, startChar), lineNum, lineText.length);
            const diagnostic = new vscode.Diagnostic(range, `[Heaven Syntax] ${message}`, vscode.DiagnosticSeverity.Error);
            diagnostic.source = 'Heaven Linter';
            diagnostics.push(diagnostic);
        }

        diagnosticCollection.set(document.uri, diagnostics);
    });
}

/**
 * Hover Provider for Heaven Natural-English constructs and ODCS primitives.
 */
const heavenHoverProvider = {
    provideHover(document, position) {
        const wordRange = document.getWordRangeAtPosition(position, /[\w-]+/);
        if (!wordRange) return null;
        const word = document.getText(wordRange);

        const hoverDocs = {
            'remember': '**Heaven Language Keyword: `remember ... as`**\n\nDeclares an immutable constant bound to the namespace.\n\n*Example:*\n```heaven\nremember STANDARD as "ODCS-2.0.0"\n```',
            'set': '**Heaven Language Keyword: `set ... to`**\n\nDeclares or mutates a variable with an expression.\n\n*Example:*\n```heaven\nset active_connections to 42\n```',
            'let': '**Heaven Language Keyword: `let ... be`**\n\nIntroduces local variable bindings.\n\n*Example:*\n```heaven\nlet quota be 100\n```',
            'increase': '**Heaven Language Keyword: `increase ... by`**\n\nIncrements a numeric variable by the specified delta.\n\n*Example:*\n```heaven\nincrease attempts by 1\n```',
            'decrease': '**Heaven Language Keyword: `decrease ... by`**\n\nDecrements a numeric variable by the specified delta.\n\n*Example:*\n```heaven\ndecrease balance by 50\n```',
            'whenever': '**Heaven Language Keyword: `whenever`**\n\nConditional branching in natural English.\n\n*Example:*\n```heaven\nwhenever count is greater than 10:\n    say "Threshold reached"\notherwise if count is equal to 10:\n    say "Exact threshold"\notherwise:\n    say "Below threshold"\n```',
            'otherwise': '**Heaven Language Keyword: `otherwise`**\n\nFallback branch for a `whenever` conditional statement.',
            'unless': '**Heaven Language Keyword: `unless`**\n\nInverted conditional statement; executes body when condition is false.\n\n*Example:*\n```heaven\nunless is_connected:\n    reconnect()\n```',
            'until': '**Heaven Language Keyword: `until`**\n\nNatural loop that repeats while condition remains false.\n\n*Example:*\n```heaven\nuntil queue.is_empty():\n    process_item(queue.pop())\n```',
            'repeat': '**Heaven Language Keyword: `repeat ... times`**\n\nHigh-performance counting loop executed exactly N times.\n\n*Example:*\n```heaven\nrepeat 5 times:\n    ping_host()\n```',
            'forever': '**Heaven Language Keyword: `forever:`**\n\nSub-millisecond infinite event loop.\n\n*Example:*\n```heaven\nforever:\n    poll_events()\n```',
            'give': '**Heaven Language Keyword: `give back`**\n\nReturns a value from a function or subroutine.\n\n*Example:*\n```heaven\ngive back total_latency\n```',
            'recover': '**Heaven Language Keyword: `recover as <err>:`**\n\nNatural exception handling block.\n\n*Example:*\n```heaven\ntry:\n    commit_block()\nrecover as err:\n    say "Handled error:", err\nalways:\n    close_socket()\n```',
            'ensure': '**Heaven Language Keyword: `ensure ... otherwise`**\n\nEvaluates invariant assertion with custom failure message.\n\n*Example:*\n```heaven\nensure balance >= 0 otherwise "Negative balance violation"\n```',
            'say': '**Heaven Language Keyword: `say`**\n\nPrints formatted output to standard console.\n\n*Example:*\n```heaven\nsay "Server running on port {port}"\n```',
            'show': '**Heaven Language Keyword: `show`**\n\nPrints expressions and inspection objects directly.\n\n*Example:*\n```heaven\nshow ledger.head_hash\n```',
            'durable': '**ODCS Layer 1: `durable record`**\n\nDefines a schema-enforced, immutable record type designed for local Write-Ahead Logging (WAL) and Zero Intent Loss.\n\n*Example:*\n```heaven\ndurable record TriageVital:\n    patient_id: String\n    heart_rate: Integer\n```',
            'checkpoint': '**ODCS Layer 1: `checkpoint`**\n\nAtomically writes a durable record into an append-only cryptographic ledger with Merkle DAG validation.\n\n*Example:*\n```heaven\ncheckpoint vital as "triage_read" into primary_ledger\n```',
            'preserve': '**ODCS Invariant: `preserve`**\n\nSeals operation intent into append-only local storage.\n\n*Example:*\n```heaven\npreserve action as "user_click" into ledger\n```',
            'verify': '**ODCS Invariant: `verify`**\n\nValidates cryptographic SHA-256 Merkle proofs against root hash.\n\n*Example:*\n```heaven\nverify asset with proof\n```',
            'ZeroIntentLoss': '**ODCS Layer 4: `ZeroIntentLoss`**\n\nMints sub-16ms tamper-evident cryptographic receipts with RFC 8785 canonical JSON serialization before upstream sockets are opened.',
            'ContinuityLedger': '**ODCS Layer 1: `ContinuityLedger`**\n\nThread-safe append-only Write-Ahead Log (WAL) that maintains cryptographic Merkle roots for bit-for-bit replayability.',
            'PNCounter': '**ODCS Layer 2: `PNCounter`**\n\nConflict-free Replicated Data Type (CRDT) Positive-Negative Counter providing Strong Eventual Consistency across partitioned nodes.',
            'Money': '**OFCS Invariant: `Money`**\n\nZero-drift high-precision decimal monetary value with strict currency matching.\n\n*Example:*\n```heaven\nset amount to Money("150.00", USD)\n```',
            'DoubleEntryRecord': '**OFCS Invariant 1: `DoubleEntryRecord`**\n\nEnforces mathematical balance: `sum(debits) == sum(credits)`.\n\n*Example:*\n```heaven\nset tx to DoubleEntryRecord("TX-101", debits=[m1], credits=[m2])\n```',
            'OFCSFinancialLedger': '**OFCS Invariant: `OFCSFinancialLedger`**\n\nTamper-evident double-entry financial ledger with cryptographic receipt tracking.',
            'HavenApp': '**Haven Backend: `HavenApp`**\n\nEnterprise microservice application container with routing, CORS, rate-limiting, and ODCS audit middleware.',
            'HavenServer': '**Haven Backend: `HavenServer`**\n\nConcurrent multi-threaded HTTP server with REST routing and ODCS continuity verification.',
            'CompletableFuture': '**Java Concurrency: `CompletableFuture`**\n\nNon-blocking reactive promise pipeline for asynchronous task composition.',
            'Transactional': '**Enterprise Annotation: `@Transactional`**\n\nEnforces atomic ledger commits on success, and mints rollback receipts on exceptions.',
            'CircuitBreaker': '**Enterprise Annotation: `@CircuitBreaker`**\n\nFault-tolerance circuit breaker preventing cascading outages across microservices.',
            'Retry': '**Enterprise Annotation: `@Retry`**\n\nResilience decorator implementing exponential backoff retries.',
            'canonical_json': '**RFC 8785 Canonical JSON**\n\nProduces deterministic, byte-for-byte canonical JSON representations of arbitrary dictionaries and primitives for SHA-256 signing.',
            'seal_hash': '**Cryptographic SHA-256 Seal**\n\nGenerates a hex-encoded SHA-256 integrity hash of any primitive, record, or buffer.'
        };

        if (hoverDocs[word]) {
            return new vscode.Hover(new vscode.MarkdownString(hoverDocs[word]));
        }
        return null;
    }
};

/**
 * Extension Activation Entry Point
 */
function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('heaven');
    context.subscriptions.push(diagnosticCollection);

    // Register Hover Provider
    context.subscriptions.push(
        vscode.languages.registerHoverProvider({ language: 'heaven' }, heavenHoverProvider)
    );

    // Status Bar Item
    heavenStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    heavenStatusBarItem.text = '$(shield) Haven v2.0';
    heavenStatusBarItem.tooltip = 'Heaven (Haven) Programming Language • ODCS-2.0.0';
    heavenStatusBarItem.command = 'heaven.showMenu';
    context.subscriptions.push(heavenStatusBarItem);

    function updateStatusBar() {
        const editor = vscode.window.activeTextEditor;
        if (editor && (editor.document.languageId === 'heaven' || editor.document.fileName.endsWith('.hvn') || editor.document.fileName.endsWith('.heaven'))) {
            heavenStatusBarItem.show();
        } else {
            heavenStatusBarItem.hide();
        }
    }
    vscode.window.onDidChangeActiveTextEditor(updateStatusBar);
    updateStatusBar();

    // Document validation listeners
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(doc => validateDocument(doc)),
        vscode.workspace.onDidOpenTextDocument(doc => validateDocument(doc))
    );

    // Validate active editor on startup
    if (vscode.window.activeTextEditor) {
        validateDocument(vscode.window.activeTextEditor.document);
    }

    // Command: heaven.run
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.run', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active Heaven source file to run.');
                return;
            }
            const { runner, python } = getHavenRunnerInfo();
            const filePath = editor.document.fileName;
            runInTerminal('🕊️ Haven Language VM', `"${python}" "${runner}" run "${filePath}"`);
        })
    );

    // Command: heaven.lint
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.lint', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active Heaven source file to lint.');
                return;
            }
            validateDocument(editor.document);
            vscode.window.showInformationMessage(`Heaven Linter: Validated ${path.basename(editor.document.fileName)}`);
        })
    );

    // Command: heaven.compile
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.compile', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active Heaven source file to compile.');
                return;
            }
            const { runner, python } = getHavenRunnerInfo();
            const filePath = editor.document.fileName;

            cp.exec(`"${python}" "${runner}" compile "${filePath}"`, (err, stdout, stderr) => {
                if (err) {
                    vscode.window.showErrorMessage(`Heaven Compilation Error: ${stderr || err.message}`);
                    return;
                }
                vscode.workspace.openTextDocument({
                    content: stdout,
                    language: 'python'
                }).then(doc => {
                    vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
                });
            });
        })
    );

    // Command: heaven.startServer
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.startServer', () => {
            const { runner, python } = getHavenRunnerInfo();
            const serverPath = path.join(path.dirname(runner), 'odcs_backend.hvn');
            runInTerminal('🕊️ ODCS Haven Gateway', `"${python}" "${runner}" run "${serverPath}"`);
            vscode.window.showInformationMessage('Starting ODCS Haven Continuity Gateway on port 8000...');
        })
    );

    // Command: heaven.repl
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.repl', () => {
            const { runner, python } = getHavenRunnerInfo();
            runInTerminal('🕊️ Haven Interactive REPL', `"${python}" "${runner}" repl`);
        })
    );

    // Command: heaven.showMenu
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.showMenu', async () => {
            const items = [
                { label: '$(play) Run Current File', description: 'Execute active .hvn file in Haven VM', cmd: 'heaven.run' },
                { label: '$(check) Validate & Lint', description: 'Run AST check for syntax correctness', cmd: 'heaven.lint' },
                { label: '$(symbol-operator) Transpile to Python IR', description: 'View compiled Python output side-by-side', cmd: 'heaven.compile' },
                { label: '$(server) Start ODCS Gateway', description: 'Launch Heaven Continuity Backend (port 8000)', cmd: 'heaven.startServer' },
                { label: '$(terminal) Interactive REPL', description: 'Launch interactive Haven command shell', cmd: 'heaven.repl' }
            ];
            const selected = await vscode.window.showQuickPick(items, { placeHolder: 'Heaven Language Operations (v2.0)' });
            if (selected) {
                vscode.commands.executeCommand(selected.cmd);
            }
        })
    );
}

function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
        diagnosticCollection.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};

