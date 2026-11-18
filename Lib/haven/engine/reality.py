"""
Ani++ / Haven OmniEngine • Polymorphic Entangled Memory Fabric (EMF)
World-First Memory Architecture with 4 Reality States:
  - Ephemeral (RAM speed)
  - Durable (Merkle WAL persistence)
  - Entangled (Peer-mesh auto-synchronization via CRDT)
  - Synthesized (Reactive cognitive evaluation)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar
import time
import copy
from haven.continuity import _GLOBAL_LEDGER

T = TypeVar("T")


class RealityState(Enum):
    EPHEMERAL = "EPHEMERAL"
    DURABLE = "DURABLE"
    ENTANGLED = "ENTANGLED"
    SYNTHESIZED = "SYNTHESIZED"


class EntangledVariable(Generic[T]):
    """
    A variable whose value is quantum-entangled across distributed peer nodes.
    When mutated locally, changes auto-disseminate to peer registries
    using Conflict-Free Replicated Data Types (CRDTs).
    """
    def __init__(self, name: str, initial_value: T, node_id: str = "local_node"):
        self.name = name
        self._value: T = initial_value
        self.node_id = node_id
        self.version = 1
        self.timestamp = time.time_ns()
        self._subscribers: List[Callable[[str, T, int], None]] = []
        _ENTANGLED_REGISTRY.register(self)

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new_val: T) -> None:
        self.set(new_val)

    def set(self, new_val: T) -> T:
        self._value = new_val
        self.version += 1
        self.timestamp = time.time_ns()
        # Broadcast to all mesh subscribers
        for sub in self._subscribers:
            try:
                sub(self.name, self._value, self.version)
            except Exception:
                pass
        _ENTANGLED_REGISTRY.broadcast(self)
        return self._value

    def on_sync(self, callback: Callable[[str, T, int], None]) -> None:
        self._subscribers.append(callback)

    def receive_remote_sync(self, remote_value: T, remote_version: int, remote_timestamp: int) -> bool:
        """Applies remote state update using Last-Write-Wins (LWW) causality."""
        if remote_timestamp > self.timestamp or (remote_timestamp == self.timestamp and remote_version > self.version):
            self._value = remote_value
            self.version = remote_version
            self.timestamp = remote_timestamp
            return True
        return False

    def __repr__(self) -> str:
        return f"EntangledVariable(name={self.name!r}, value={self._value!r}, v={self.version})"


class SynthesizedVariable(Generic[T]):
    """
    A variable that does not store static state, but continuously synthesizes its value
    via a cognitive reactive evaluator function and dependent inputs.
    """
    def __init__(self, name: str, evaluator: Callable[[], T], cache_ttl_s: float = 0.0):
        self.name = name
        self.evaluator = evaluator
        self.cache_ttl_s = cache_ttl_s
        self._last_val: Optional[T] = None
        self._last_evaluated: float = 0.0

    @property
    def value(self) -> T:
        now = time.time()
        if self.cache_ttl_s > 0 and (now - self._last_evaluated) < self.cache_ttl_s:
            return self._last_val  # type: ignore

        res = self.evaluator()
        self._last_val = res
        self._last_evaluated = now
        return res

    def __call__(self) -> T:
        return self.value

    def __repr__(self) -> str:
        return f"SynthesizedVariable(name={self.name!r}, value={self.value!r})"


class DurableVariable(Generic[T]):
    """
    A variable guaranteed to never lose intent across crashes or power loss.
    Every update is automatically journaled and sealed into the Merkle ledger.
    """
    def __init__(self, name: str, initial_value: T, ledger=None):
        self.name = name
        self._value: T = initial_value
        self.ledger = ledger or _GLOBAL_LEDGER
        self.version = 1
        # Commit genesis value
        self._commit_to_ledger("INIT")

    def _commit_to_ledger(self, action: str):
        payload = {
            "entity": "DurableVariable",
            "name": self.name,
            "value": str(self._value),
            "version": self.version,
            "action": action,
            "timestamp": time.time_ns()
        }
        self.ledger.append(payload)

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new_val: T) -> None:
        self.set(new_val)

    def set(self, new_val: T) -> T:
        self._value = new_val
        self.version += 1
        self._commit_to_ledger("UPDATE")
        return self._value

    def __repr__(self) -> str:
        return f"DurableVariable(name={self.name!r}, value={self._value!r}, v={self.version})"


class EntangledRegistry:
    """Registry managing all entangled variables within the local node process."""
    def __init__(self):
        self._vars: Dict[str, EntangledVariable] = {}
        self._mesh_listeners: List[Callable[[Dict[str, Any]], None]] = []

    def register(self, var: EntangledVariable) -> None:
        self._vars[var.name] = var

    def get(self, name: str) -> Optional[EntangledVariable]:
        return self._vars.get(name)

    def broadcast(self, var: EntangledVariable) -> None:
        packet = {
            "name": var.name,
            "value": var.value,
            "version": var.version,
            "timestamp": var.timestamp,
            "node_id": var.node_id
        }
        for listener in self._mesh_listeners:
            try:
                listener(packet)
            except Exception:
                pass

    def add_mesh_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        self._mesh_listeners.append(listener)

    def ingest_remote_packet(self, packet: Dict[str, Any]) -> bool:
        name = packet.get("name")
        if name in self._vars:
            return self._vars[name].receive_remote_sync(
                packet["value"], packet["version"], packet["timestamp"]
            )
        return False


_ENTANGLED_REGISTRY = EntangledRegistry()


def entangled(name: str, value: Any, node_id: str = "node-alpha") -> EntangledVariable:
    """Convenience helper to declare an Entangled variable."""
    return EntangledVariable(name, value, node_id=node_id)


def synthesized(name: str, evaluator: Callable[[], Any], cache_ttl_s: float = 0.0) -> SynthesizedVariable:
    """Convenience helper to declare a Synthesized variable."""
    return SynthesizedVariable(name, evaluator, cache_ttl_s=cache_ttl_s)


def durable_var(name: str, value: Any, ledger=None) -> DurableVariable:
    """Convenience helper to declare a Durable variable."""
    return DurableVariable(name, value, ledger=ledger)
