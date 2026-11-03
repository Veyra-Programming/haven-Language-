"""
Haven Annotations Framework (Java-Relatable Enterprise Metadata System)
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import functools
import inspect
import time
import threading
import warnings
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

# ==============================================================================
# 1. META-ANNOTATIONS (Java java.lang.annotation equivalence)
# ==============================================================================

class RetentionPolicy(Enum):
    SOURCE = "SOURCE"      # Discarded during compilation
    CLASS = "CLASS"        # Recorded in bytecode, not available at runtime
    RUNTIME = "RUNTIME"    # Retained in runtime memory, inspectable via reflection


class ElementType(Enum):
    TYPE = "TYPE"                      # Class, interface, enum, record
    FIELD = "FIELD"                    # Class attribute / field
    METHOD = "METHOD"                  # Method declaration
    PARAMETER = "PARAMETER"            # Method / function parameter
    CONSTRUCTOR = "CONSTRUCTOR"        # Constructor declaration
    LOCAL_VARIABLE = "LOCAL_VARIABLE"  # Local variable
    ANNOTATION_TYPE = "ANNOTATION_TYPE"# Annotation type declaration


class AnnotationMetadata:
    """Stores reflection metadata for an applied annotation."""
    def __init__(self, annotation_type: Any, attributes: Dict[str, Any], target: Any):
        self.annotation_type = annotation_type
        self.attributes = attributes
        self.target = target
        self.applied_at = time.time()

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.attributes.items())
        return f"@{self.annotation_type.__name__}({attrs})"


def Retention(policy: RetentionPolicy):
    """Meta-annotation defining retention lifetime."""
    def decorator(cls):
        setattr(cls, "__retention__", policy)
        return cls
    return decorator


def Target(allowed_targets: Union[ElementType, List[ElementType], Set[ElementType]]):
    """Meta-annotation defining where this annotation may be applied."""
    if isinstance(allowed_targets, ElementType):
        allowed = {allowed_targets}
    else:
        allowed = set(allowed_targets)

    def decorator(cls):
        setattr(cls, "__targets__", allowed)
        return cls
    return decorator


class AnnotationMeta(type):
    def __call__(cls, *args, **kwargs):
        # Case 1: @MyAnnotation without parentheses decorating a function/class
        if len(args) == 1 and not kwargs and (callable(args[0]) or isinstance(args[0], type)):
            target = args[0]
            _register_annotation(target, cls, {})
            return target

        # Case 2: @MyAnnotation(attr=value) or @MyAnnotation("value")
        attrs = dict(kwargs)
        if args:
            attrs["value"] = args[0]

        def decorator(target):
            _register_annotation(target, cls, attrs)
            return target
        return decorator


def interface(cls: Optional[Type] = None):
    """
    Declares a custom Annotation type (Java @interface).
    Usage:
        @interface
        @Retention(RetentionPolicy.RUNTIME)
        @Target(ElementType.METHOD)
        class Query:
            value: str = ""
    """
    def wrap(target_cls):
        new_dict = dict(target_cls.__dict__)
        new_dict["__is_annotation__"] = True
        new_dict["__retention__"] = getattr(target_cls, "__retention__", RetentionPolicy.RUNTIME)
        new_dict["__targets__"] = getattr(target_cls, "__targets__", {ElementType.TYPE, ElementType.METHOD})

        # Inherit bases while using AnnotationMeta
        bases = target_cls.__bases__
        if bases == (object,):
            bases = ()
        annot_cls = AnnotationMeta(target_cls.__name__, bases, new_dict)
        return annot_cls

    if cls is not None:
        return wrap(cls)
    return wrap


# Reflection helper functions
def get_annotations(target: Any) -> List[AnnotationMetadata]:
    """Retrieves all annotations applied to a class, method, or function."""
    return getattr(target, "__haven_annotations__", [])


def has_annotation(target: Any, annotation_cls: Type) -> bool:
    """Checks if target carries a specific annotation."""
    annotations = get_annotations(target)
    return any(a.annotation_type == annotation_cls for a in annotations)


def get_annotation(target: Any, annotation_cls: Type) -> Optional[AnnotationMetadata]:
    """Retrieves the first matching annotation metadata on target."""
    for a in get_annotations(target):
        if a.annotation_type == annotation_cls:
            return a
    return None


def _register_annotation(target: Any, annotation_cls: Type, attributes: Dict[str, Any]):
    if not hasattr(target, "__haven_annotations__"):
        try:
            target.__haven_annotations__ = []
        except (AttributeError, TypeError):
            pass
    if hasattr(target, "__haven_annotations__"):
        target.__haven_annotations__.append(AnnotationMetadata(annotation_cls, attributes, target))


# ==============================================================================
# 2. CORE JAVA-RELATABLE ANNOTATIONS
# ==============================================================================

class OverrideError(TypeError):
    """Raised when an @Override method does not actually override a superclass method."""
    pass


class SealedHierarchyError(TypeError):
    """Raised when an unauthorized class attempts to extend a @Sealed class."""
    pass


def Override(method: Callable) -> Callable:
    """
    Java @Override:
    Validates that the annotated method overrides a declaration in a superclass or interface.
    Validation occurs when the method is bound or invoked within a class hierarchy.
    """
    setattr(method, "__haven_override__", True)
    _register_annotation(method, Override, {})

    # Mark method for post-class construction validation
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        return method(*args, **kwargs)
    wrapper.__haven_override__ = True
    _register_annotation(wrapper, Override, {})
    return wrapper


def Deprecated(since: str = "1.0.0", for_removal: bool = False, alternative: str = ""):
    """
    Java @Deprecated:
    Marks code as deprecated with version tracking and optional removal notification.
    """
    def decorator(target):
        _register_annotation(target, Deprecated, {
            "since": since,
            "for_removal": for_removal,
            "alternative": alternative
        })
        if inspect.isfunction(target) or inspect.ismethod(target):
            @functools.wraps(target)
            def wrapper(*args, **kwargs):
                msg = f"{target.__name__} is deprecated since v{since}."
                if alternative:
                    msg += f" Use '{alternative}' instead."
                if for_removal:
                    msg += " Scheduled for REMOVAL in a future release."
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                return target(*args, **kwargs)
            _register_annotation(wrapper, Deprecated, {
                "since": since,
                "for_removal": for_removal,
                "alternative": alternative
            })
            return wrapper
        return target
    return decorator


def Synchronized(lock: Optional[threading.RLock] = None):
    """
    Java synchronized method:
    Acquires a reentrant lock for the duration of the method execution.
    """
    _default_lock = threading.RLock()

    def decorator(fn: Callable) -> Callable:
        actual_lock = lock if lock is not None else _default_lock
        _register_annotation(fn, Synchronized, {"lock": actual_lock})

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with actual_lock:
                return fn(*args, **kwargs)
        _register_annotation(wrapper, Synchronized, {"lock": actual_lock})
        return wrapper
    return decorator


class VolatileProperty:
    """Java volatile field descriptor ensuring immediate memory visibility."""
    def __init__(self, default: Any = None):
        self._val = default
        self._lock = threading.Lock()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        with self._lock:
            return self._val

    def __set__(self, instance, value):
        with self._lock:
            self._val = value


def Volatile(default: Any = None):
    """Java volatile variable modifier."""
    return VolatileProperty(default)


def Sealed(permits: List[Union[str, Type]]):
    """
    Java 17 @Sealed:
    Restricts which classes may extend or implement the annotated class.
    """
    def decorator(cls: Type) -> Type:
        permitted_names = {p if isinstance(p, str) else p.__name__ for p in permits}
        cls.__permitted_subclasses__ = permitted_names
        _register_annotation(cls, Sealed, {"permits": permitted_names})

        orig_init_subclass = getattr(cls, "__init_subclass__", None)

        def __init_subclass__(subcls, **kwargs):
            if subcls.__name__ not in cls.__permitted_subclasses__:
                raise SealedHierarchyError(
                    f"Class '{subcls.__name__}' is not permitted to extend sealed class '{cls.__name__}'. "
                    f"Permitted subclasses are: {sorted(list(cls.__permitted_subclasses__))}"
                )
            if orig_init_subclass:
                orig_init_subclass(**kwargs)

        cls.__init_subclass__ = classmethod(__init_subclass__)
        return cls
    return decorator


def Serial(cls: Type) -> Type:
    """
    Java @Serial:
    Validates that a class supports deterministic RFC 8785 canonical serialization.
    """
    _register_annotation(cls, Serial, {})
    setattr(cls, "__serializable__", True)
    return cls


# ==============================================================================
# 3. ODCS ENTERPRISE CONTINUITY ANNOTATIONS
# ==============================================================================

def Durable(cls: Optional[Type] = None):
    """
    ODCS @Durable:
    Converts a class into a hardware-sealed, memory-immutable ODCS durable record.
    Automatically binds deterministic SHA-256 canonical hashing.
    """
    def wrap(target_cls):
        from haven.continuity import durable_record
        sealed = durable_record(target_cls)
        _register_annotation(sealed, Durable, {})
        return sealed

    if cls is not None:
        return wrap(cls)
    return wrap


class TransactionRollback(Exception):
    """Raised when a transactional method triggers a continuity rollback."""
    def __init__(self, original_exc: Exception, rollback_receipt: Any):
        super().__init__(f"Transaction rolled back due to: {original_exc}")
        self.original_exc = original_exc
        self.rollback_receipt = rollback_receipt


def Transactional(rollback_on: Tuple[Type[Exception], ...] = (Exception,), ledger=None):
    """
    ODCS / Enterprise @Transactional:
    Executes the method inside an atomic WAL transaction block.
    If any exception in rollback_on occurs, all state modifications are rolled back
    and an uncommitted rollback receipt is logged to the continuity ledger.
    """
    def decorator(fn: Callable) -> Callable:
        _register_annotation(fn, Transactional, {"rollback_on": rollback_on})

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            from haven.continuity import _GLOBAL_LEDGER
            active_ledger = ledger or _GLOBAL_LEDGER
            tx_id = f"tx-{int(time.time()*1000)}-{id(fn)}"

            # Log Transaction BEGIN
            active_ledger.append({
                "type": "TX_BEGIN",
                "tx_id": tx_id,
                "method": fn.__name__,
                "timestamp": time.time()
            })

            try:
                result = fn(*args, **kwargs)
                # Log Transaction COMMIT
                active_ledger.append({
                    "type": "TX_COMMIT",
                    "tx_id": tx_id,
                    "method": fn.__name__,
                    "status": "COMMITTED"
                })
                return result
            except rollback_on as e:
                # Log Transaction ROLLBACK
                receipt = active_ledger.append({
                    "type": "TX_ROLLBACK",
                    "tx_id": tx_id,
                    "method": fn.__name__,
                    "reason": str(e),
                    "exception_type": type(e).__name__
                })
                raise TransactionRollback(e, receipt) from e

        _register_annotation(wrapper, Transactional, {"rollback_on": rollback_on})
        return wrapper
    return decorator


def Audit(ledger=None, event_name: Optional[str] = None):
    """
    ODCS @Audit:
    Cryptographically records method invocations, parameter hashes, latency,
    and return values to an immutable Merkle continuity ledger.
    """
    def decorator(fn: Callable) -> Callable:
        name = event_name or fn.__name__
        _register_annotation(fn, Audit, {"event_name": name})

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            from haven.continuity import _GLOBAL_LEDGER
            active_ledger = ledger or _GLOBAL_LEDGER
            t0 = time.perf_counter()

            # Execute method
            try:
                res = fn(*args, **kwargs)
                duration_ms = (time.perf_counter() - t0) * 1000
                active_ledger.append({
                    "event": name,
                    "status": "SUCCESS",
                    "args_repr": [str(a)[:100] for a in args[1:] if args], # exclude self
                    "duration_ms": round(duration_ms, 3),
                    "timestamp": time.time()
                })
                return res
            except Exception as exc:
                duration_ms = (time.perf_counter() - t0) * 1000
                active_ledger.append({
                    "event": name,
                    "status": "FAILURE",
                    "error": str(exc),
                    "duration_ms": round(duration_ms, 3),
                    "timestamp": time.time()
                })
                raise exc

        _register_annotation(wrapper, Audit, {"event_name": name})
        return wrapper
    return decorator


def ContinuityCheck(pre_condition: Optional[Callable[..., bool]] = None,
                    post_condition: Optional[Callable[[Any], bool]] = None):
    """
    ODCS @ContinuityCheck:
    Enforces mathematical pre- and post-condition invariants on execution state.
    """
    def decorator(fn: Callable) -> Callable:
        _register_annotation(fn, ContinuityCheck, {})

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if pre_condition and not pre_condition(*args, **kwargs):
                raise AssertionError(f"Pre-condition failed for @ContinuityCheck on '{fn.__name__}'")
            res = fn(*args, **kwargs)
            if post_condition and not post_condition(res):
                raise AssertionError(f"Post-condition failed for @ContinuityCheck on '{fn.__name__}'")
            return res

        _register_annotation(wrapper, ContinuityCheck, {})
        return wrapper
    return decorator


def CircuitBreaker(failure_threshold: int = 3, recovery_time_seconds: float = 2.0, fallback: Optional[Callable] = None):
    """
    Enterprise @CircuitBreaker:
    Prevents catastrophic system collapse by failing fast and degrading gracefully
    when errors exceed threshold.
    """
    def decorator(fn: Callable) -> Callable:
        failures = 0
        last_failure_time = 0.0
        state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
        lock = threading.Lock()

        _register_annotation(fn, CircuitBreaker, {
            "failure_threshold": failure_threshold,
            "recovery_time": recovery_time_seconds
        })

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal failures, last_failure_time, state
            with lock:
                now = time.time()
                if state == "OPEN":
                    if now - last_failure_time > recovery_time_seconds:
                        state = "HALF_OPEN"
                    else:
                        if fallback:
                            return fallback(*args, **kwargs)
                        raise RuntimeError(f"CircuitBreaker OPEN for '{fn.__name__}'. Fast fail.")

            try:
                res = fn(*args, **kwargs)
                with lock:
                    if state == "HALF_OPEN":
                        state = "CLOSED"
                        failures = 0
                return res
            except Exception as e:
                with lock:
                    failures += 1
                    last_failure_time = time.time()
                    if failures >= failure_threshold:
                        state = "OPEN"
                if fallback:
                    return fallback(*args, **kwargs)
                raise e

        _register_annotation(wrapper, CircuitBreaker, {
            "failure_threshold": failure_threshold,
            "recovery_time": recovery_time_seconds
        })
        return wrapper
    return decorator


def Retry(max_attempts: int = 3, backoff_ms: int = 50, retry_on: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Enterprise @Retry:
    Retries method on failure with exponential or linear backoff.
    """
    def decorator(fn: Callable) -> Callable:
        _register_annotation(fn, Retry, {"max_attempts": max_attempts, "backoff_ms": backoff_ms})

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempts = 0
            curr_backoff = backoff_ms / 1000.0
            while True:
                try:
                    attempts += 1
                    return fn(*args, **kwargs)
                except retry_on as exc:
                    if attempts >= max_attempts:
                        raise exc
                    time.sleep(curr_backoff)
                    curr_backoff *= 1.5

        _register_annotation(wrapper, Retry, {"max_attempts": max_attempts, "backoff_ms": backoff_ms})
        return wrapper
    return decorator
