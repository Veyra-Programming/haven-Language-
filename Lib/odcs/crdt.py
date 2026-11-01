"""
Open Digital Continuity Standard (ODCS) - Layer 2: Conflict-Free Replicated Data Types (CRDTs)
Standard Specification & Architecture by Anirudha Puthraya.
Implements:
  - VectorClock: Distributed logical clock for causality tracking
  - LWWRegister: Last-Write-Wins Register with timestamp arbitration
  - PNCounter: Positive-Negative Distributed Counter
  - AWORSet: Add-Wins Observed-Removed Set
  - OutboxPipeline: Store-and-forward queue with automatic synchronization
"""

from typing import Any, Dict, List, Set, Tuple, Optional
import time
import uuid
import copy
from .envelope import canonical_json, compute_sha256


class VectorClock:
    """
    Logical Vector Clock for causality tracking across distributed nodes (ODCS Layer 2.1).
    Maintains [node_id -> counter] mapping.
    """
    def __init__(self, clock_dict: Optional[Dict[str, int]] = None):
        self.clock: Dict[str, int] = dict(clock_dict) if clock_dict else {}

    def tick(self, node_id: str) -> int:
        """Increment the logical clock for this node."""
        self.clock[node_id] = self.clock.get(node_id, 0) + 1
        return self.clock[node_id]

    def increment(self, node_id: str) -> int:
        """Alias for tick."""
        return self.tick(node_id)

    def merge(self, other: "VectorClock") -> "VectorClock":
        """Merge another vector clock: max(local, remote) for all keys."""
        all_nodes = set(self.clock.keys()).union(other.clock.keys())
        merged = {}
        for n in all_nodes:
            merged[n] = max(self.clock.get(n, 0), other.clock.get(n, 0))
        return VectorClock(merged)

    def get(self, node_id: str, default: int = 0) -> int:
        return self.clock.get(node_id, default)

    def __getitem__(self, node_id: str) -> int:
        return self.clock.get(node_id, 0)

    def __setitem__(self, node_id: str, value: int) -> None:
        self.clock[node_id] = value

    def causally_precedes(self, other: "VectorClock") -> bool:
        """Returns True if this vector clock is strictly in the causal past of other."""
        less_equal = all(self.clock.get(n, 0) <= other.clock.get(n, 0) for n in self.clock)
        strictly_less = any(self.clock.get(n, 0) < other.clock.get(n, 0) for n in other.clock)
        return less_equal and strictly_less

    def to_dict(self) -> Dict[str, int]:
        return dict(self.clock)

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "VectorClock":
        return cls(data)

    def is_concurrent(self, other: "VectorClock") -> bool:
        """Returns True if neither clock causally precedes the other (concurrent update)."""
        return not self.causally_precedes(other) and not other.causally_precedes(self) and self.clock != other.clock

    def to_dict(self) -> Dict[str, int]:
        return dict(self.clock)

    def __repr__(self) -> str:
        return f"VectorClock({self.clock})"


class LWWRegister:
    """
    Last-Write-Wins Register (ODCS Layer 2.2).
    Resolves concurrent field mutations using a physical timestamp and tie-breaking node_id.
    """
    def __init__(self, value: Any, timestamp: Optional[float] = None, node_id: str = "node-0"):
        self.value = value
        self.timestamp = timestamp or time.time()
        self.node_id = node_id

    def set(self, value: Any, node_id: Optional[str] = None) -> None:
        """Update value with new timestamp."""
        self.value = value
        self.timestamp = time.time()
        if node_id:
            self.node_id = node_id

    def merge(self, other: "LWWRegister") -> "LWWRegister":
        """Merge with remote register. Winner is highest timestamp; tie breaker is higher node_id."""
        if other.timestamp > self.timestamp:
            return LWWRegister(other.value, other.timestamp, other.node_id)
        elif other.timestamp == self.timestamp:
            winner = other if other.node_id >= self.node_id else self
            return LWWRegister(winner.value, winner.timestamp, winner.node_id)
        return LWWRegister(self.value, self.timestamp, self.node_id)

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value, "timestamp": self.timestamp, "node_id": self.node_id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LWWRegister":
        return cls(data.get("value"), data.get("timestamp", 0.0), data.get("node_id", "local"))

    def __repr__(self) -> str:
        return f"LWWRegister({repr(self.value)} @ {self.timestamp:.4f} by {self.node_id})"


class PNCounter:
    """
    Positive-Negative Counter (ODCS Layer 2.2).
    Enables increment and decrement operations across distributed nodes that converge without coordination.
    """
    def __init__(self, node_id: str = "local"):
        self.node_id = node_id
        self.p: Dict[str, int] = {}
        self.n: Dict[str, int] = {}

    def inc(self, value: int = 1) -> None:
        """Increment counter on local node."""
        self.p[self.node_id] = self.p.get(self.node_id, 0) + value

    def dec(self, value: int = 1) -> None:
        """Decrement counter on local node."""
        self.n[self.node_id] = self.n.get(self.node_id, 0) + value

    def increment(self, node_id_or_val: Any = None, value: int = 1) -> None:
        """Ergonomic alias for inc; supports increment(val) or increment(node_id, val)."""
        if isinstance(node_id_or_val, str):
            node_id = node_id_or_val
            self.p[node_id] = self.p.get(node_id, 0) + value
        elif isinstance(node_id_or_val, (int, float)):
            self.inc(int(node_id_or_val))
        else:
            self.inc(1)

    def decrement(self, node_id_or_val: Any = None, value: int = 1) -> None:
        """Ergonomic alias for dec; supports decrement(val) or decrement(node_id, val)."""
        if isinstance(node_id_or_val, str):
            node_id = node_id_or_val
            self.n[node_id] = self.n.get(node_id, 0) + value
        elif isinstance(node_id_or_val, (int, float)):
            self.dec(int(node_id_or_val))
        else:
            self.dec(1)

    @property
    def value(self) -> int:
        """Current converged counter value."""
        return sum(self.p.values()) - sum(self.n.values())

    def merge(self, other: "PNCounter") -> "PNCounter":
        """Merge with remote counter: takes pointwise max of P and N maps."""
        result = PNCounter(self.node_id)
        all_p = set(self.p.keys()).union(other.p.keys())
        all_n = set(self.n.keys()).union(other.n.keys())
        for k in all_p:
            result.p[k] = max(self.p.get(k, 0), other.p.get(k, 0))
        for k in all_n:
            result.n[k] = max(self.n.get(k, 0), other.n.get(k, 0))
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {"node_id": self.node_id, "p": dict(self.p), "n": dict(self.n)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PNCounter":
        cnt = cls(data.get("node_id", "local"))
        cnt.p = dict(data.get("p", {}))
        cnt.n = dict(data.get("n", {}))
        return cnt

    def __repr__(self) -> str:
        return f"PNCounter(value={self.value}, +={dict(self.p)}, -={dict(self.n)})"


class AWORSet:
    """
    Add-Wins Observed-Removed Set (ODCS Layer 2.2).
    Concurrent additions take precedence over deletions.
    Elements are tracked with unique birth tags.
    """
    def __init__(self):
        # element -> set of unique tag ids
        self.add_set: Dict[Any, Set[str]] = {}
        # set of tag ids removed
        self.remove_set: Set[str] = set()

    def add(self, element: Any) -> str:
        """Add element with unique tag."""
        tag = uuid.uuid4().hex[:12]
        if element not in self.add_set:
            self.add_set[element] = set()
        self.add_set[element].add(tag)
        return tag

    def remove(self, element: Any) -> None:
        """Remove observed tags for this element."""
        if element in self.add_set:
            self.remove_set.update(self.add_set[element])

    def contains(self, element: Any) -> bool:
        """Returns True if at least one unremoved tag exists for this element."""
        if element not in self.add_set:
            return False
        remaining = self.add_set[element] - self.remove_set
        return len(remaining) > 0

    @property
    def elements(self) -> List[Any]:
        """List of active set elements."""
        return [e for e in self.add_set if self.contains(e)]

    def merge(self, other: "AWORSet") -> "AWORSet":
        """Merge two sets by unioning add sets and remove sets."""
        result = AWORSet()
        all_elements = set(self.add_set.keys()).union(other.add_set.keys())
        for e in all_elements:
            result.add_set[e] = self.add_set.get(e, set()).union(other.add_set.get(e, set()))
        result.remove_set = self.remove_set.union(other.remove_set)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "add_set": {k: list(v) for k, v in self.add_set.items()},
            "remove_set": list(self.remove_set)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AWORSet":
        s = cls()
        s.add_set = {k: set(v) for k, v in data.get("add_set", {}).items()}
        s.remove_set = set(data.get("remove_set", []))
        return s

    def __repr__(self) -> str:
        return f"AWORSet({self.elements})"


class OutboxPipeline:
    """
    Store-and-Forward Outbox Orchestrator (ODCS Layer 2.3).
    Buffers local mutations in a persistent queue, tracking ACK confirmations and retry states.
    """
    def __init__(self, name: str = "primary_outbox", max_batch_size: int = 50):
        self.name = name
        self.max_batch_size = max_batch_size
        self.queue: List[Dict[str, Any]] = []
        self.delivered: List[Dict[str, Any]] = []

    def enqueue(self, action: str, payload: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Stage a mutation in the outbox."""
        op_id = uuid.uuid4().hex[:16]
        entry = {
            "op_id": op_id,
            "mutation_id": op_id,
            "action": action,
            "payload": payload,
            "metadata": metadata or {},
            "timestamp": time.time(),
            "status": "pending",
            "attempts": 0,
        }
        self.queue.append(entry)
        return op_id

    def stage(self, payload: Any, action: str = "MUTATION", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Convenience method to stage mutation into outbox."""
        return self.enqueue(action=action, payload=payload, metadata=metadata)

    def pull_batch(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Extracts batch of staged mutations up to limit."""
        batch_limit = limit or self.max_batch_size
        return list(self.queue[:batch_limit])

    def acknowledge(self, mutation_ids: List[str]) -> int:
        """Acknowledges and removes confirmed mutations from the pending outbox."""
        ack_set = set(mutation_ids)
        new_queue = []
        acked_count = 0
        now = time.time()
        for item in self.queue:
            m_id = item.get("mutation_id") or item.get("op_id")
            if m_id in ack_set:
                item["status"] = "delivered"
                item["delivered_at"] = now
                self.delivered.append(item)
                acked_count += 1
            else:
                new_queue.append(item)
        self.queue = new_queue
        return acked_count

    @property
    def has_pending(self) -> bool:
        return len(self.queue) > 0

    @property
    def _queue(self) -> List[Dict[str, Any]]:
        return self.queue

    def flush_sync(self, handler) -> int:
        """
        Attempts to deliver all pending items through handler(entry).
        If handler returns True, item is marked delivered.
        """
        success_count = 0
        remaining = []
        for item in self.queue:
            item["attempts"] += 1
            try:
                ok = handler(item)
                if ok:
                    item["status"] = "delivered"
                    item["delivered_at"] = time.time()
                    self.delivered.append(item)
                    success_count += 1
                else:
                    remaining.append(item)
            except Exception:
                remaining.append(item)
        self.queue = remaining
        return success_count

    @property
    def pending_count(self) -> int:
        return len(self.queue)

    @property
    def delivered_count(self) -> int:
        return len(self.delivered)
