/**
 * 🦊 Haven Programming Language (ODCS Native Edition) - Visual Studio Code Extension
 * 
 * Features:
 *  - Official Haven Fox Mascot & Visual Branding
 *  - High-Speed Grammar & Syntax Highlighting
 *  - Real-Time AST Linting & Error Diagnostics
 *  - Contextual Hover Tooltips with Keyword Uses & Invariant Explanations
 *  - Dynamic Autocompletion Provider for Keywords, Primitives & Annotations
 *  - Intelligent Signature Help for Builtins & Functions
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
 * Hover Documentation Catalog
 */
const hoverDocs = {
    'set': '**Haven Language Keyword: `set ... to`**\n\nSets or mutates state in natural English.\n\n*Example:*\n```haven\nset active_connections to 42\n```',
    'let': '**Haven Language Keyword: `let ... be`**\n\nBinds local variables.\n\n*Example:*\n```haven\nlet rate be 0.05\n```',
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
    'Money': '**OFCS Invariant: `Money`**\n\nZero-drift high-precision decimal monetary value with strict currency safety.\n\n*Example:*\n```haven\nset amount to Money("150.00", USD)\n```',
    'DoubleEntryRecord': '**OFCS Invariant 1: `DoubleEntryRecord`**\n\nEnforces mathematical double-entry balance: `sum(debits) == sum(credits)`.\n\n*Example:*\n```haven\nset tx to DoubleEntryRecord("TX-101", debits=[m1], credits=[m2])\n```',
    'OFCSFinancialLedger': '**OFCS Invariant: `OFCSFinancialLedger`**\n\nTamper-evident double-entry financial ledger with cryptographic receipt tracking.',
    'HavenApp': '**Haven Backend: `HavenApp`**\n\nEnterprise microservice application container with routing, CORS, rate-limiting, and ODCS audit middleware.',
    'HavenServer': '**Haven Backend: `HavenServer`**\n\nConcurrent multi-threaded HTTP server with REST routing and ODCS continuity verification.',
    'CompletableFuture': '**Java Concurrency: `CompletableFuture`**\n\nNon-blocking reactive promise pipeline for asynchronous task composition.',
    'Transactional': '**Enterprise Annotation: `@Transactional`**\n\nEnforces atomic ledger commits on success, and mints rollback receipts on exceptions.',
    'CircuitBreaker': '**Enterprise Annotation: `@CircuitBreaker`**\n\nFault-tolerance circuit breaker preventing cascading outages across microservices.',
    'Retry': '**Enterprise Annotation: `@Retry`**\n\nResilience decorator implementing exponential backoff retries.'
};

/**
 * Autocompletion Catalog
 */
const HAVEN_AUTOCOMPLETE_ITEMS = [
    // Keywords
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
    { label: 'durable record', detail: 'durable record <Name>:', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('durable record ${1:AssetRecord}:\n    def __init__(self, ${2:asset_id}, ${3:value}):\n        self.${2:asset_id} = ${2:asset_id}\n        self.${3:value} = ${3:value}') },
    // Types & Classes
    { label: 'Money', detail: 'Money(amount, currency=USD)', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('Money("${1:100.00}", ${2:USD})') },
    { label: 'DoubleEntryRecord', detail: 'DoubleEntryRecord(tx_id, debits, credits)', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('DoubleEntryRecord("${1:TX-1001}", debits=[${2:m1}], credits=[${3:m2}])') },
    { label: 'FinancialAccount', detail: 'FinancialAccount(account_id, currency)', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('FinancialAccount("${1:ACC-101}", currency=${2:USD})') },
    { label: 'OFCSFinancialLedger', detail: 'OFCSFinancialLedger(ledger_name)', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('OFCSFinancialLedger(ledger_name="${1:primary_vault}")') },
    { label: 'HavenApp', detail: 'HavenApp(name, port=8080)', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('HavenApp(name="${1:Microservice}", port=${2:8080}, cors=True, continuity_audit=True)') },
    { label: 'HavenServer', detail: 'HavenServer(host, port, router)', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('HavenServer(host="${1:127.0.0.1}", port=${2:8080})') },
    { label: 'Router', detail: 'Router()', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('Router()') },
    { label: 'Response.json', detail: 'Response.json(data, status_code=200)', kind: vscode.CompletionItemKind.Method, insertText: new vscode.SnippetString('Response.json(${1:data})') },
    { label: 'Response.ok', detail: 'Response.ok(message, data=None)', kind: vscode.CompletionItemKind.Method, insertText: new vscode.SnippetString('Response.ok("${1:OK}")') },
    { label: 'CompletableFuture.supply_async', detail: 'CompletableFuture.supply_async(supplier)', kind: vscode.CompletionItemKind.Method, insertText: new vscode.SnippetString('CompletableFuture.supply_async(lambda: ${1:task()})') },
    { label: 'AtomicInteger', detail: 'AtomicInteger(initial=0)', kind: vscode.CompletionItemKind.Class, insertText: new vscode.SnippetString('AtomicInteger(${1:0})') },
    // Annotations
    { label: '@Transactional', detail: '@Transactional(rollback_on=(Exception,), audit=True)', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Transactional(rollback_on=(Exception,), audit=True)') },
    { label: '@CircuitBreaker', detail: '@CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@CircuitBreaker(failure_threshold=${1:5}, recovery_timeout=${2:30.0})') },
    { label: '@Retry', detail: '@Retry(max_attempts=3, backoff_factor=2.0)', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Retry(max_attempts=${1:3}, backoff_factor=${2:2.0})') },
    { label: '@FinancialTransaction', detail: '@FinancialTransaction', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@FinancialTransaction') },
    { label: '@Idempotent', detail: '@Idempotent(key_field="tx_id")', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Idempotent') },
    { label: '@ZeroDrift', detail: '@ZeroDrift', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@ZeroDrift') },
    { label: '@Override', detail: '@Override', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Override') },
    { label: '@Sealed', detail: '@Sealed(permits=(...))', kind: vscode.CompletionItemKind.Snippet, insertText: new vscode.SnippetString('@Sealed(permits=(${1:SubClass}))') }
];

/**
 * Signature Catalog
 */
const HAVEN_SIGNATURES = {
    'checkpoint': {
        label: 'checkpoint(asset: Any, alias: str = None, ledger: ContinuityLedger = None) -> LedgerEntry',
        doc: 'ODCS Invariant: Seals asset state into local append-only Merkle ledger.'
    },
    'Money': {
        label: 'Money(amount: Union[str, int, float, Decimal], currency: Currency = USD) -> Money',
        doc: 'OFCS Invariant: Zero-drift decimal currency representation with exact arithmetic.'
    },
    'DoubleEntryRecord': {
        label: 'DoubleEntryRecord(tx_id: str, debits: List[Money], credits: List[Money]) -> DoubleEntryRecord',
        doc: 'OFCS Invariant 1: sum(debits) == sum(credits). Prevents unbalanced transactions.'
    },
    'HavenApp': {
        label: 'HavenApp(name: str = "HavenApplication", host: str = "127.0.0.1", port: int = 8080) -> HavenApp',
        doc: 'Enterprise Haven Microservice Application Container with built-in ODCS verification endpoints.'
    },
    'HavenServer': {
        label: 'HavenServer(host: str = "127.0.0.1", port: int = 8080, router: Optional[Router] = None) -> HavenServer',
        doc: 'High-Performance Concurrent Multi-Threaded HTTP Server.'
    }
};

/**
 * Extension Activation Entry Point
 */
function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('haven');
    context.subscriptions.push(diagnosticCollection);

    // Register Hover Provider
    context.subscriptions.push(
        vscode.languages.registerHoverProvider({ language: 'heaven' }, {
            provideHover(document, position) {
                const wordRange = document.getWordRangeAtPosition(position, /[\w-]+/);
                if (!wordRange) return null;
                const word = document.getText(wordRange);
                if (hoverDocs[word]) {
                    return new vscode.Hover(new vscode.MarkdownString(hoverDocs[word]));
                }
                return null;
            }
        })
    );

    // Register Dynamic Completion Provider
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            { language: 'heaven' },
            {
                provideCompletionItems(document, position) {
                    return HAVEN_AUTOCOMPLETE_ITEMS;
                }
            },
            '.', '@'
        )
    );

    // Register Signature Help Provider
    context.subscriptions.push(
        vscode.languages.registerSignatureHelpProvider(
            { language: 'heaven' },
            {
                provideSignatureHelp(document, position) {
                    const lineText = document.lineAt(position.line).text.substring(0, position.character);
                    for (const [funcName, sigData] of Object.entries(HAVEN_SIGNATURES)) {
                        if (lineText.includes(funcName + '(')) {
                            const help = new vscode.SignatureHelp();
                            const sig = new vscode.SignatureInformation(sigData.label, new vscode.MarkdownString(sigData.doc));
                            help.signatures = [sig];
                            help.activeSignature = 0;
                            help.activeParameter = 0;
                            return help;
                        }
                    }
                    return null;
                }
            },
            '(', ','
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
        if (editor && (editor.document.languageId === 'heaven' || editor.document.fileName.endsWith('.hvn') || editor.document.fileName.endsWith('.haven'))) {
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
            runInTerminal('🦊 Haven Test Runner', `"${havenExe}" -m haven.cli test`);
        })
    );

    // Command: heaven.lint
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.lint', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active Haven source file to lint.');
                return;
            }
            validateDocument(editor.document);
            vscode.window.showInformationMessage(`🦊 Haven Fox Linter: Validated ${path.basename(editor.document.fileName)}`);
        })
    );

    // Command: heaven.compile
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.compile', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active Haven source file to inspect.');
                return;
            }
            const { havenExe } = getHavenRunnerInfo();
            const filePath = editor.document.fileName;
            runInTerminal('🦊 Haven Disassembler', `"${havenExe}" -m dis "${filePath}"`);
        })
    );

    // Command: heaven.startServer
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.startServer', () => {
            const { havenExe } = getHavenRunnerInfo();
            runInTerminal('🦊 Haven Microservice', `"${havenExe}" -c "from haven import HavenApp; app = HavenApp(); app.run(blocking=True)"`);
            vscode.window.showInformationMessage('🦊 Starting Haven ODCS Server on port 8080...');
        })
    );

    // Command: heaven.repl
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.repl', () => {
            const { havenExe } = getHavenRunnerInfo();
            runInTerminal('🦊 Haven REPL', `"${havenExe}"`);
        })
    );

    // Command: heaven.showMenu
    context.subscriptions.push(
        vscode.commands.registerCommand('heaven.showMenu', async () => {
            const items = [
                { label: '🦊 Run Active File', description: 'Execute current file in Haven VM', cmd: 'heaven.run' },
                { label: '🧪 Run Test Suites', description: 'Run complete 100% green test suite (haven test)', cmd: 'heaven.test' },
                { label: '🔍 Validate & Lint', description: 'Inspect AST and syntax invariants', cmd: 'heaven.lint' },
                { label: '⚡ View Bytecode Disassembly', description: 'Inspect compiled Haven VM instructions', cmd: 'heaven.compile' },
                { label: '🌐 Launch Backend Server', description: 'Start high-speed Haven microservice', cmd: 'heaven.startServer' },
                { label: '💻 Interactive REPL', description: 'Launch interactive Haven shell', cmd: 'heaven.repl' }
            ];
            const selected = await vscode.window.showQuickPick(items, { placeHolder: '🦊 Haven Language Operations' });
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
