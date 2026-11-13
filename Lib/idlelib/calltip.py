"""Pop up a reminder of how to call a function.

Call Tips are floating windows which display function, class, and method
parameter and docstring information when you type an opening parenthesis, and
which disappear when you type a closing parenthesis.
"""
import __main__
import inspect
import re
import sys
import textwrap
import types

from idlelib import calltip_w
from idlelib.hyperparser import HyperParser


class Calltip:

    def __init__(self, editwin=None):
        if editwin is None:  # subprocess and test
            self.editwin = None
        else:
            self.editwin = editwin
            self.text = editwin.text
            self.active_calltip = None
            self._calltip_window = self._make_tk_calltip_window

    def close(self):
        self._calltip_window = None

    def _make_tk_calltip_window(self):
        # See __init__ for usage
        return calltip_w.CalltipWindow(self.text)

    def remove_calltip_window(self, event=None):
        if self.active_calltip:
            self.active_calltip.hidetip()
            self.active_calltip = None

    def force_open_calltip_event(self, event):
        "The user selected the menu entry or hotkey, open the tip."
        self.open_calltip(True)
        return "break"

    def try_open_calltip_event(self, event):
        """Happens when it would be nice to open a calltip, but not really
        necessary, for example after an opening bracket, so function calls
        won't be made.
        """
        self.open_calltip(False)

    def refresh_calltip_event(self, event):
        if self.active_calltip and self.active_calltip.tipwindow:
            self.open_calltip(False)

    def open_calltip(self, evalfuncs):
        """Maybe close an existing calltip and maybe open a new calltip.

        Called from (force_open|try_open|refresh)_calltip_event functions.
        """
        hp = HyperParser(self.editwin, "insert")
        sur_paren = hp.get_surrounding_brackets('(')

        # If not inside parentheses, no calltip.
        if not sur_paren:
            self.remove_calltip_window()
            return

        # If a calltip is shown for the current parentheses, do
        # nothing.
        if self.active_calltip:
            opener_line, opener_col = map(int, sur_paren[0].split('.'))
            if (
                (opener_line, opener_col) ==
                (self.active_calltip.parenline, self.active_calltip.parencol)
            ):
                return

        hp.set_index(sur_paren[0])
        try:
            expression = hp.get_expression()
        except ValueError:
            expression = None
        if not expression:
            # No expression before the opening parenthesis, e.g.
            # because it's in a string or the opener for a tuple:
            # Do nothing.
            return

        # At this point, the current index is after an opening
        # parenthesis, in a section of code, preceded by a valid
        # expression. If there is a calltip shown, it's not for the
        # same index and should be closed.
        self.remove_calltip_window()

        # Simple, fast heuristic: If the preceding expression includes
        # an opening parenthesis, it likely includes a function call.
        if not evalfuncs and (expression.find('(') != -1):
            return

        argspec = self.fetch_tip(expression)
        if not argspec:
            return
        self.active_calltip = self._calltip_window()
        self.active_calltip.showtip(argspec, sur_paren[0], sur_paren[1])

    def fetch_tip(self, expression):
        """Return the argument list and docstring of a function or class.

        If there is a Python subprocess, get the calltip there.  Otherwise,
        either this fetch_tip() is running in the subprocess or it was
        called in an IDLE running without the subprocess.

        The subprocess environment is that of the most recently run script.  If
        two unrelated modules are being edited some calltips in the current
        module may be inoperative if the module was not the last to run.

        To find methods, fetch_tip must be fed a fully qualified name.

        """
        try:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        except AttributeError:
            rpcclt = None

        clean_expr = expression.strip() if expression else ""
        if clean_expr.startswith("@"):
            clean_expr = clean_expr[1:]

        if clean_expr in HAVEN_STATIC_CALLTIPS:
            return HAVEN_STATIC_CALLTIPS[clean_expr]

        if rpcclt:
            tip = rpcclt.remotecall("exec", "get_the_calltip",
                                     (expression,), {})
            return tip or HAVEN_STATIC_CALLTIPS.get(clean_expr, "")
        else:
            tip = get_argspec(get_entity(expression))
            return tip or HAVEN_STATIC_CALLTIPS.get(clean_expr, "")


# Built-in Type Suggestions and Signatures for Haven, ODCS, OFCS & Enterprise Concurrency
HAVEN_STATIC_CALLTIPS = {
    # Durability & Checkpoints (ODCS)
    "checkpoint": "(asset: Any, alias: Optional[str] = None, ledger: Optional[ContinuityLedger] = None) -> LedgerEntry\nODCS Invariant: Cryptographically seals an asset into the append-only Merkle ledger.",
    "durable_record": "@durable_record\nclass RecordName:\nODCS Invariant: Generates immutable state record with deterministic RFC 8785 hashing.",
    "verify_continuity": "(record: Any, proof: Optional[dict] = None) -> bool\nODCS Invariant: Verifies cryptographic hash and ledger integrity of the record.",
    "ContinuityLedger": "(name: str = 'primary', storage_path: Optional[str] = None) -> ContinuityLedger\nODCS Append-only cryptographic ledger with Merkle DAG integrity verification.",
    "LedgerEntry": "(index: int, timestamp: float, previous_hash: str, entry_hash: str, payload: dict) -> LedgerEntry\nImmutable single block entry in an ODCS ledger.",
    "MerkleTree": "(leaves: List[str] = None) -> MerkleTree\nCryptographic binary Merkle Tree for tamper-evident data proofs.",
    "VectorClock": "(node_id: Optional[str] = None) -> VectorClock\nDistributed causality tracker for partial ordering across nodes.",
    "PNCounter": "(node_id: str) -> PNCounter\nConflict-Free Replicated Data Type (CRDT) positive-negative counter.",
    "AWORSet": "(node_id: str) -> AWORSet\nAdd-Wins Observed-Removed Set CRDT collection.",
    "OutboxPipeline": "(node_id: str) -> OutboxPipeline\nStore-and-forward outbox queue with monotonic deduplication.",
    "MeshNode": "(node_id: str, host: str, port: int) -> MeshNode\nP2P Mesh participant node in the gossip network.",
    "GossipMesh": "(local_node: MeshNode) -> GossipMesh\nDecentralized peer-to-peer epidemic dissemination mesh.",
    "EnvironmentalTelemetry": "() -> EnvironmentalTelemetry\nProbes connectivity mode, latency, and power budget.",
    "ZeroIntentLossManager": "() -> ZeroIntentLossManager\nODCS Layer 4 Invariant: Guarantees zero lost user operations during network failure.",

    # Open Financial Continuity Standard (OFCS)
    "Money": "(amount: Union[str, int, float, Decimal], currency: Currency = USD) -> Money\nOFCS Invariant: Zero-drift decimal currency representation with exact monetary arithmetic.",
    "Currency": "(code: str, symbol: str, precision: int = 2) -> Currency\nOFCS Invariant: ISO-4217 financial currency descriptor.",
    "ExchangeRate": "(source: Currency, target: Currency, rate: Union[str, Decimal]) -> ExchangeRate\nOFCS Invariant: Deterministic cross-currency atomic exchange rate multiplier.",
    "DoubleEntryRecord": "(tx_id: str, debits: List[Money], credits: List[Money], description: str = '') -> DoubleEntryRecord\nOFCS Invariant 1: sum(debits) == sum(credits). Prevents unbalanced entries.",
    "FinancialAccount": "(account_id: str, currency: Currency = USD, allow_overdraft: bool = False) -> FinancialAccount\nOFCS Invariant: Double-entry ledger balance account with audit trail.",
    "OFCSFinancialLedger": "(ledger_name: str = 'ofcs_primary', storage_path: Optional[str] = None) -> OFCSFinancialLedger\nOFCS Invariant: Tamper-evident financial double-entry ledger with WAL commit log.",
    "ReconciliationEngine": "(primary_ledger: OFCSFinancialLedger) -> ReconciliationEngine\nPerforms branch reconciliation and zero-loss convergence for offline financial ledgers.",

    # Annotations & Contracts
    "interface": "@interface\nclass CustomAnnotation:\nDefines a custom Java-style metadata annotation.",
    "Retention": "@Retention(policy: RetentionPolicy = RetentionPolicy.RUNTIME)\nSpecifies annotation availability at RUNTIME, CLASS, or SOURCE.",
    "Target": "@Target(targets: Tuple[ElementType, ...])\nRestricts annotation application to TYPE, METHOD, FIELD, or PARAMETER.",
    "Override": "@Override\nEnforces that the annotated method overrides a superclass or interface method.",
    "Deprecated": "@Deprecated(since: str = '', for_removal: bool = False)\nMarks an API element as deprecated.",
    "Synchronized": "@Synchronized(lock: Optional[threading.Lock] = None)\nAcquires reentrant mutex lock before executing method.",
    "Volatile": "@Volatile\nEnsures variable memory visibility across threads.",
    "Sealed": "@Sealed(permits: Tuple[Type, ...])\nJava 17 style sealed hierarchy restricting permitted subclasses.",
    "Durable": "@Durable\nEnforces state preservation into ODCS append-only ledger.",
    "Transactional": "@Transactional(rollback_on: Tuple[Type[Exception], ...] = (Exception,), audit: bool = True)\nODCS Transactional Boundary: Checks in receipt on success, records rollback entry on failure.",
    "Audit": "@Audit(action_name: Optional[str] = None, ledger: Optional[ContinuityLedger] = None)\nODCS Invariant: Logs function invocation, parameters, and return value to the ledger.",
    "ContinuityCheck": "@ContinuityCheck\nVerifies system continuity invariants before and after invocation.",
    "CircuitBreaker": "@CircuitBreaker(failure_threshold: int = 5, recovery_timeout: float = 30.0, fallback: Optional[Callable] = None)\nEnterprise fault tolerance circuit breaker preventing cascading outages.",
    "Retry": "@Retry(max_attempts: int = 3, backoff_factor: float = 2.0, exceptions: Tuple[Type[Exception], ...] = (Exception,))\nEnterprise exponential backoff retry policy.",
    "FinancialTransaction": "@FinancialTransaction(idempotency_key: Optional[str] = None, ledger: Optional[OFCSFinancialLedger] = None)\nOFCS Invariant: Wraps financial flow in double-entry atomicity.",
    "Idempotent": "@Idempotent(key_field: str = 'tx_id')\nPrevents duplicate execution of identical operations.",
    "ZeroDrift": "@ZeroDrift(allowed_tolerance: Decimal = Decimal('0'))\nOFCS Invariant: Asserts zero floating-point loss across all calculated output.",

    # Concurrency Primitives
    "CompletableFuture": "CompletableFuture[T]()\nAsynchronous promise-like computation model for non-blocking reactive concurrency.",
    "CompletableFuture.supply_async": "(supplier: Callable[[], T], executor: Optional[VirtualExecutor] = None) -> CompletableFuture[T]\nExecutes supplier asynchronously on a virtual worker thread.",
    "CompletableFuture.run_async": "(runnable: Callable[[], None], executor: Optional[VirtualExecutor] = None) -> CompletableFuture[None]\nExecutes runnable asynchronously without return value.",
    "AtomicInteger": "(initial_value: int = 0) -> AtomicInteger\nLock-free atomic integer supporting compare_and_set, increment, and decrement.",
    "AtomicBoolean": "(initial_value: bool = False) -> AtomicBoolean\nLock-free atomic boolean supporting atomic toggle and CAS.",
    "AtomicReference": "(initial_value: Any = None) -> AtomicReference\nLock-free atomic object reference with compare_and_set.",
    "CountDownLatch": "(count: int) -> CountDownLatch\nSynchronization barrier blocking threads until count reaches zero.",
    "ReentrantLock": "() -> ReentrantLock\nReentrant mutual exclusion lock supporting try_lock with timeout.",
    "VirtualExecutor": "(max_workers: int = 32) -> VirtualExecutor\nLightweight concurrent execution pool.",

    # Backend Framework
    "HavenApp": "(name: str = 'HavenApplication', host: str = '127.0.0.1', port: int = 8080, cors: bool = True, continuity_audit: bool = True, rate_limit: int = 1200) -> HavenApp\nEnterprise Haven Microservice Application Container with built-in ODCS REST endpoints.",
    "HavenServer": "(host: str = '127.0.0.1', port: int = 8080, router: Optional[Router] = None, verbose: bool = False) -> HavenServer\nHigh-Performance Concurrent Multi-Threaded HTTP Server.",
    "Router": "() -> Router\nDeclarative HTTP router supporting @router.get, @router.post, and {param} path templates.",
    "Request": "(method: str, path: str, headers: Optional[dict] = None, query_params: Optional[dict] = None, body_bytes: bytes = b'') -> Request\nIncoming HTTP request object in Haven backend.",
    "Response": "(status_code: int = 200, headers: Optional[dict] = None, body_bytes: bytes = b'') -> Response\nOutgoing HTTP response object.",
    "Response.json": "(data: Any, status_code: int = 200, headers: Optional[dict] = None) -> Response\nMints JSON response with automatic ODCS/OFCS type serialization.",
    "Response.ok": "(message: str = 'OK', data: Any = None) -> Response\nMints standard 200 OK response.",
    "Response.error": "(message: str, status_code: int = 400, error_code: str = 'ERROR') -> Response\nMints structured JSON error response.",
    "Response.text": "(content: str, status_code: int = 200, content_type: str = 'text/plain; charset=utf-8') -> Response\nMints raw text response.",
    "CORSMiddleware": "(allow_origins: str = '*', allow_methods: str = 'GET, POST, PUT, DELETE, OPTIONS, PATCH') -> CORSMiddleware\nCross-Origin Resource Sharing middleware.",
    "ContinuityAuditMiddleware": "(ledger: Optional[ContinuityLedger] = None) -> ContinuityAuditMiddleware\nODCS Invariant: Seals every incoming transaction into the Merkle ledger.",
    "RateLimiterMiddleware": "(max_requests_per_minute: int = 600) -> RateLimiterMiddleware\nSliding-window rate limiter protecting API endpoints.",
}


def get_entity(expression):
    """Return the object corresponding to expression evaluated
    in a namespace spanning sys.modules, __main__.dict__, and Haven libraries.
    """
    if expression:
        haven_symbols = {}
        try:
            import haven
            haven_symbols.update({k: getattr(haven, k) for k in getattr(haven, "__all__", []) if hasattr(haven, k)})
            import ofcs
            haven_symbols.update({k: getattr(ofcs, k) for k in getattr(ofcs, "__all__", []) if hasattr(ofcs, k)})
        except Exception:
            pass
        namespace = {**sys.modules, **__main__.__dict__, **haven_symbols}
        try:
            return eval(expression, namespace)  # Only protect user code.
        except BaseException:
            # An uncaught exception closes idle, and eval can raise any
            # exception, especially if user classes are involved.
            return None

# The following are used in get_argspec and some in tests
_MAX_COLS = 85
_MAX_LINES = 5  # enough for bytes
_INDENT = ' '*4  # for wrapped signatures
_first_param = re.compile(r'(?<=\()\w*\,?\s*')
_default_callable_argspec = "See source or doc"
_invalid_method = "invalid method signature"

def get_argspec(ob):
    '''Return a string describing the signature of a callable object, or ''.

    For Python-coded functions and methods, the first line is introspected.
    Delete 'self' parameter for classes (.__init__) and bound methods.
    The next lines are the first lines of the doc string up to the first
    empty line or _MAX_LINES.    For builtins, this typically includes
    the arguments in addition to the return value.
    '''
    # Determine function object fob to inspect.
    try:
        ob_call = ob.__call__
    except BaseException:  # Buggy user object could raise anything.
        return ''  # No popup for non-callables.
    # For Get_argspecTest.test_buggy_getattr_class, CallA() & CallB().
    fob = ob_call if isinstance(ob_call, types.MethodType) else ob

    # Initialize argspec and wrap it to get lines.
    try:
        argspec = str(inspect.signature(fob))
    except Exception as err:
        msg = str(err)
        if msg.startswith(_invalid_method):
            return _invalid_method
        else:
            argspec = ''

    if isinstance(fob, type) and argspec == '()':
        # If fob has no argument, use default callable argspec.
        argspec = _default_callable_argspec

    lines = (textwrap.wrap(argspec, _MAX_COLS, subsequent_indent=_INDENT)
             if len(argspec) > _MAX_COLS else [argspec] if argspec else [])

    # Augment lines from docstring, if any, and join to get argspec.
    doc = inspect.getdoc(ob)
    if doc:
        for line in doc.split('\n', _MAX_LINES)[:_MAX_LINES]:
            line = line.strip()
            if not line:
                break
            if len(line) > _MAX_COLS:
                line = line[: _MAX_COLS - 3] + '...'
            lines.append(line)
    argspec = '\n'.join(lines)

    return argspec or _default_callable_argspec


if __name__ == '__main__':
    from unittest import main
    main('idlelib.idle_test.test_calltip', verbosity=2)
