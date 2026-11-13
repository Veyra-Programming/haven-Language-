"""
Haven Concurrency & Reactive Primitives (java.util.concurrent equivalence)
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Implements core Java concurrency constructs:
  1. CompletableFuture (Fluent async reactive pipelines)
  2. Atomic Variables (AtomicInteger, AtomicBoolean, AtomicReference)
  3. Synchronization Constructs (CountDownLatch, ReentrantLock)
  4. Virtual Execution & Task Pools (VirtualExecutor)
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Generic

T = TypeVar("T")
U = TypeVar("U")

# Shared thread pool for virtual asynchronous operations
_GLOBAL_EXECUTOR = ThreadPoolExecutor(max_workers=32, thread_name_prefix="HavenWorker")


# ==============================================================================
# 1. COMPLETABLE FUTURE (Java CompletableFuture)
# ==============================================================================

class CompletableFuture(Generic[T]):
    """
    Java java.util.concurrent.CompletableFuture equivalence:
    Enables declarative, non-blocking asynchronous pipeline chaining.
    """
    def __init__(self, value: Optional[T] = None, completed: bool = False):
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._value: Optional[T] = value
        self._exception: Optional[Exception] = None
        self._is_completed: bool = completed
        if completed:
            self._event.set()

    @classmethod
    def completed_future(cls, value: T) -> "CompletableFuture[T]":
        """Returns a new CompletableFuture already completed with the given value."""
        return cls(value=value, completed=True)

    @classmethod
    def supply_async(cls, supplier: Callable[[], T], executor=None) -> "CompletableFuture[T]":
        """Executes supplier asynchronously and returns a CompletableFuture."""
        cf = cls()
        exec_pool = executor or _GLOBAL_EXECUTOR

        def task():
            try:
                res = supplier()
                cf.complete(res)
            except Exception as e:
                cf.complete_exceptionally(e)

        exec_pool.submit(task)
        return cf

    def complete(self, value: T) -> bool:
        """Completes the future with the given value."""
        with self._lock:
            if self._is_completed:
                return False
            self._value = value
            self._is_completed = True
            self._event.set()
            return True

    def complete_exceptionally(self, exception: Exception) -> bool:
        """Completes the future with an exception."""
        with self._lock:
            if self._is_completed:
                return False
            self._exception = exception
            self._is_completed = True
            self._event.set()
            return True

    def get(self, timeout: Optional[float] = None) -> T:
        """Waits if necessary for the computation to complete and returns result."""
        if not self._event.wait(timeout=timeout):
            raise TimeoutError("CompletableFuture timed out waiting for result")
        if self._exception is not None:
            raise self._exception
        return self._value

    def join(self) -> T:
        """Returns the result value when complete, raising unhandled exceptions directly."""
        return self.get()

    def is_done(self) -> bool:
        return self._is_completed

    def then_apply(self, fn: Callable[[T], U]) -> "CompletableFuture[U]":
        """
        Java .thenApply(fn):
        Chains a transformation function on the result of this stage.
        """
        next_cf = CompletableFuture[U]()

        def callback():
            try:
                val = self.get()
                res = fn(val)
                next_cf.complete(res)
            except Exception as e:
                next_cf.complete_exceptionally(e)

        _GLOBAL_EXECUTOR.submit(callback)
        return next_cf

    def then_accept(self, action: Callable[[T], None]) -> "CompletableFuture[None]":
        """
        Java .thenAccept(consumer):
        Consumes the result of this stage without returning a new value.
        """
        return self.then_apply(action)

    def then_compose(self, fn: Callable[[T], "CompletableFuture[U]"]) -> "CompletableFuture[U]":
        """
        Java .thenCompose(fn):
        FlatMaps the result into another CompletableFuture.
        """
        next_cf = CompletableFuture[U]()

        def callback():
            try:
                val = self.get()
                sub_cf = fn(val)
                res = sub_cf.get()
                next_cf.complete(res)
            except Exception as e:
                next_cf.complete_exceptionally(e)

        _GLOBAL_EXECUTOR.submit(callback)
        return next_cf

    def exceptionally(self, fallback_fn: Callable[[Exception], T]) -> "CompletableFuture[T]":
        """
        Java .exceptionally(fn):
        Catches any exception in the chain and recovers with fallback value.
        """
        next_cf = CompletableFuture[T]()

        def callback():
            self._event.wait()
            if self._exception is not None:
                try:
                    res = fallback_fn(self._exception)
                    next_cf.complete(res)
                except Exception as e:
                    next_cf.complete_exceptionally(e)
            else:
                next_cf.complete(self._value)

        _GLOBAL_EXECUTOR.submit(callback)
        return next_cf

    @classmethod
    def all_of(cls, *futures: "CompletableFuture") -> "CompletableFuture[List[Any]]":
        """
        Java CompletableFuture.allOf:
        Completes when all given futures have completed.
        """
        combined = cls()

        def wait_all():
            results = []
            for f in futures:
                try:
                    results.append(f.get())
                except Exception as e:
                    combined.complete_exceptionally(e)
                    return
            combined.complete(results)

        _GLOBAL_EXECUTOR.submit(wait_all)
        return combined


# ==============================================================================
# 2. ATOMIC VARIABLES (java.util.concurrent.atomic equivalence)
# ==============================================================================

class AtomicInteger:
    """Java AtomicInteger: Thread-safe atomic 32/64-bit integer."""
    def __init__(self, initial_value: int = 0):
        self._val = int(initial_value)
        self._lock = threading.Lock()

    def get(self) -> int:
        with self._lock:
            return self._val

    def set(self, new_value: int) -> None:
        with self._lock:
            self._val = int(new_value)

    def get_and_set(self, new_value: int) -> int:
        with self._lock:
            old = self._val
            self._val = int(new_value)
            return old

    def compare_and_set(self, expect: int, update: int) -> bool:
        """CAS (Compare-And-Swap) operation."""
        with self._lock:
            if self._val == expect:
                self._val = int(update)
                return True
            return False

    def get_and_increment(self) -> int:
        return self.get_and_add(1)

    def increment_and_get(self) -> int:
        return self.add_and_get(1)

    def get_and_decrement(self) -> int:
        return self.get_and_add(-1)

    def decrement_and_get(self) -> int:
        return self.add_and_get(-1)

    def get_and_add(self, delta: int) -> int:
        with self._lock:
            old = self._val
            self._val += delta
            return old

    def add_and_get(self, delta: int) -> int:
        with self._lock:
            self._val += delta
            return self._val

    def __repr__(self) -> str:
        return f"AtomicInteger({self.get()})"


class AtomicBoolean:
    """Java AtomicBoolean: Thread-safe atomic boolean flag."""
    def __init__(self, initial_value: bool = False):
        self._val = bool(initial_value)
        self._lock = threading.Lock()

    def get(self) -> bool:
        with self._lock:
            return self._val

    def set(self, new_val: bool):
        with self._lock:
            self._val = bool(new_val)

    def compare_and_set(self, expect: bool, update: bool) -> bool:
        with self._lock:
            if self._val == expect:
                self._val = bool(update)
                return True
            return False

    def get_and_set(self, new_val: bool) -> bool:
        with self._lock:
            old = self._val
            self._val = bool(new_val)
            return old

    def __repr__(self) -> str:
        return f"AtomicBoolean({self.get()})"


class AtomicReference(Generic[T]):
    """Java AtomicReference: Thread-safe object reference with atomic CAS."""
    def __init__(self, initial_value: Optional[T] = None):
        self._val: Optional[T] = initial_value
        self._lock = threading.Lock()

    def get(self) -> Optional[T]:
        with self._lock:
            return self._val

    def set(self, new_value: Optional[T]) -> None:
        with self._lock:
            self._val = new_value

    def compare_and_set(self, expect: Optional[T], update: Optional[T]) -> bool:
        with self._lock:
            if self._val is expect or self._val == expect:
                self._val = update
                return True
            return False

    def get_and_set(self, new_value: Optional[T]) -> Optional[T]:
        with self._lock:
            old = self._val
            self._val = new_value
            return old

    def __repr__(self) -> str:
        return f"AtomicReference({self.get()!r})"


# ==============================================================================
# 3. SYNCHRONIZATION CONSTRUCTS (CountDownLatch, ReentrantLock)
# ==============================================================================

class CountDownLatch:
    """
    Java java.util.concurrent.CountDownLatch equivalence:
    Allows one or more threads to wait until a set of operations completes.
    """
    def __init__(self, count: int):
        if count < 0:
            raise ValueError("Count cannot be negative")
        self._count = count
        self._lock = threading.Condition()

    def count_down(self):
        with self._lock:
            if self._count > 0:
                self._count -= 1
                if self._count == 0:
                    self._lock.notify_all()

    def get_count(self) -> int:
        with self._lock:
            return self._count

    def await_latch(self, timeout: Optional[float] = None) -> bool:
        """Blocks until count reaches zero or timeout expires."""
        with self._lock:
            if self._count == 0:
                return True
            return self._lock.wait_for(lambda: self._count == 0, timeout=timeout)

    # Alias to Java syntax
    await_ = await_latch


class ReentrantLock:
    """Java ReentrantLock: Mutual exclusion lock with reentrant acquisition."""
    def __init__(self):
        self._rlock = threading.RLock()

    def lock(self):
        self._rlock.acquire()

    def unlock(self):
        self._rlock.release()

    def try_lock(self, timeout: float = 0.0) -> bool:
        return self._rlock.acquire(timeout=timeout)

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unlock()


# ==============================================================================
# 4. VIRTUAL EXECUTOR (Java Virtual Threads & ExecutorService)
# ==============================================================================

class VirtualExecutor:
    """
    Java Virtual Thread ExecutorService:
    Submits and manages asynchronous parallel tasks.
    """
    def __init__(self, max_workers: int = 16):
        self._pool = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, fn: Callable, *args, **kwargs) -> CompletableFuture:
        return CompletableFuture.supply_async(lambda: fn(*args, **kwargs), executor=self._pool)

    def shutdown(self, wait: bool = True):
        self._pool.shutdown(wait=wait)

