"""
Haven Reactive Living Stream & Event Flow Engine (HavenFlow)
Standard: Open Digital Continuity Standard (ODCS) Real-Time Data Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides reactive data streams, functional sliding windows, backpressure,
and seamless streaming into ODCS cryptographic write-ahead ledgers.
"""

from typing import Callable, Any, List, Optional, Iterator, Iterable
from .continuity import checkpoint


class Flow:
    """
    A reactive data pipeline stream that natively integrates with Haven's
    pipeline operator `|>`.
    """
    def __init__(self, source_iterable: Iterable[Any]):
        self._source = source_iterable

    def __iter__(self) -> Iterator[Any]:
        return iter(self._source)

    def map(self, fn: Callable[[Any], Any]) -> 'Flow':
        def _gen():
            for item in self:
                yield fn(item)
        return Flow(_gen())

    def filter(self, predicate: Callable[[Any], bool]) -> 'Flow':
        def _gen():
            for item in self:
                if predicate(item):
                    yield item
        return Flow(_gen())

    def window(self, size: int) -> 'Flow':
        """Groups elements into fixed-size tumbling chunks."""
        def _gen():
            buf = []
            for item in self:
                buf.append(item)
                if len(buf) == size:
                    yield list(buf)
                    buf = []
            if buf:
                yield list(buf)
        return Flow(_gen())

    def sliding_window(self, size: int, step: int = 1) -> 'Flow':
        """Groups elements into overlapping sliding windows."""
        def _gen():
            items = list(self)
            for i in range(0, len(items) - size + 1, step):
                yield items[i : i + size]
        return Flow(_gen())

    def collect(self) -> List[Any]:
        return list(self)

    def reduce(self, reducer: Callable[[Any, Any], Any], initial: Any) -> Any:
        accum = initial
        for item in self:
            accum = reducer(accum, item)
        return accum

    def checkpoint_into(self, ledger: Optional[Any] = None, alias: str = "flow_batch") -> List[Any]:
        """Checkpoints all elements or batches into an ODCS continuity ledger."""
        results = []
        for idx, item in enumerate(self):
            entry_alias = f"{alias}_{idx + 1}"
            checkpoint(item, alias=entry_alias, ledger=ledger)
            results.append(item)
        return results

    # Support pipeline operator: data |> flow
    def __ror__(self, other: Iterable[Any]) -> 'Flow':
        return Flow(other)


# Pipeline Helper Functions for `|>` syntax
def flow_of(items: Iterable[Any]) -> Flow:
    return Flow(items)

def flow_map(fn: Callable[[Any], Any]) -> Callable[[Flow], Flow]:
    return lambda f: f.map(fn) if isinstance(f, Flow) else Flow(f).map(fn)

def flow_filter(predicate: Callable[[Any], bool]) -> Callable[[Flow], Flow]:
    return lambda f: f.filter(predicate) if isinstance(f, Flow) else Flow(f).filter(predicate)

def flow_window(size: int) -> Callable[[Flow], Flow]:
    return lambda f: f.window(size) if isinstance(f, Flow) else Flow(f).window(size)

def flow_collect(f: Flow) -> List[Any]:
    return f.collect() if isinstance(f, Flow) else list(f)


class EventStream:
    """
    Publish-Subscribe reactive event broker with queue buffers and history replay.
    """
    def __init__(self, name: str, buffer_capacity: int = 1000):
        self.name = name
        self.buffer_capacity = buffer_capacity
        self.subscribers: List[Callable[[Any], None]] = []
        self.history: List[Any] = []

    def subscribe(self, callback: Callable[[Any], None]) -> None:
        self.subscribers.append(callback)

    def publish(self, event: Any) -> None:
        self.history.append(event)
        if len(self.history) > self.buffer_capacity:
            self.history.pop(0)

        for sub in self.subscribers:
            try:
                sub(event)
            except Exception:
                pass

    def as_flow(self) -> Flow:
        return Flow(list(self.history))
