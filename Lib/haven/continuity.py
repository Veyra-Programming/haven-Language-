"""
Haven Core: Open Digital Continuity Standard (ODCS) Implementation
Copyright (c) 2026 Anirudha Puthraya.
"""

import time
import inspect
from typing import Any, Dict, List, Optional
from .immutability import ContinuityImmutabilityError, canonical_json_bytes, sha256_digest
from .merkle import MerkleTree

class DurableRecord:
    """
    Native base class for sealed ODCS records.
    Inherited types cannot mutate attributes post initialization.
    """
    __slots__ = ("_odcs_sealed", "_merkle", "_hash", "__dict__")

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)
        self._seal()

    def _seal(self) -> None:
        state_repr = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        merkle = MerkleTree(state_repr)
        object.__setattr__(self, "_merkle", merkle)
        object.__setattr__(self, "_hash", merkle.root)
        object.__setattr__(self, "_odcs_sealed", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_odcs_sealed", False):
            raise ContinuityImmutabilityError(
                f"Modification rejected: Record '{self.__class__.__name__}' is sealed under ODCS v1.0.0 standards."
            )
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if getattr(self, "_odcs_sealed", False):
            raise ContinuityImmutabilityError(
                f"Attribute deletion rejected: Record '{self.__class__.__name__}' is sealed."
            )
        object.__delattr__(self, name)

    def odcs_hash(self) -> str:
        """Returns the cryptographically sealed root hash."""
        return self._hash

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


def durable_record(cls):
    """Decorator synthesizing dynamic classes into durable ODCS entities."""
    original_init = cls.__init__

    def wrapped_init(self, *args, **kwargs):
        object.__setattr__(self, "_odcs_sealed", False)
        
        annotations = getattr(cls, '__annotations__', {})
        if original_init == object.__init__ and annotations:
            ann_keys = list(annotations.keys())
            for i, val in enumerate(args):
                if i < len(ann_keys):
                    setattr(self, ann_keys[i], val)
            for k, v in kwargs.items():
                setattr(self, k, v)
        elif original_init != object.__init__:
            sig = inspect.signature(original_init)
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()
            for k, v in bound.arguments.items():
                if k != "self":
                    setattr(self, k, v)
            original_init(self, *args, **kwargs)
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        # Build integrity tree
        state = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        tree = MerkleTree(state)
        object.__setattr__(self, "_merkle", tree)
        object.__setattr__(self, "_hash", tree.root)
        object.__setattr__(self, "_odcs_sealed", True)

    cls.__init__ = wrapped_init
    cls.__setattr__ = DurableRecord.__setattr__
    cls.__delattr__ = DurableRecord.__delattr__
    cls.odcs_hash = lambda self: self._hash
    cls.to_dict = lambda self: {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
    return cls


class LedgerEntry:
    __slots__ = ("index", "timestamp", "asset_id", "payload_hash", "prev_hash", "entry_hash")

    def __init__(self, index: int, asset_id: str, payload_hash: str, prev_hash: str):
        self.index = index
        self.timestamp = time.time_ns()
        self.asset_id = asset_id
        self.payload_hash = payload_hash
        self.prev_hash = prev_hash
        self.entry_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        block = {
            "index": self.index,
            "timestamp": self.timestamp,
            "asset_id": self.asset_id,
            "payload_hash": self.payload_hash,
            "prev_hash": self.prev_hash
        }
        return sha256_digest(block)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "asset_id": self.asset_id,
            "payload_hash": self.payload_hash,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash
        }


class ContinuityLedger:
    """
    Append-only tamper-evident state ledger.
    Maintains cryptographic hash chain verification.
    """
    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, name: str):
        self.name: str = name
        self.chain: List[LedgerEntry] = []
        self.head_hash: str = self.GENESIS_HASH

    def commit(self, asset: Any, alias: Optional[str] = None) -> LedgerEntry:
        asset_id = alias or f"asset_{len(self.chain)}"
        if hasattr(asset, "odcs_hash"):
            payload_hash = asset.odcs_hash()
        else:
            payload_hash = sha256_digest(asset)
            
        entry = LedgerEntry(
            index=len(self.chain),
            asset_id=asset_id,
            payload_hash=payload_hash,
            prev_hash=self.head_hash
        )
        self.chain.append(entry)
        self.head_hash = entry.entry_hash
        return entry

    def verify_integrity(self) -> bool:
        """Audits every block in the chain to verify unbroken hash linkage."""
        expected_prev = self.GENESIS_HASH
        for entry in self.chain:
            if entry.prev_hash != expected_prev:
                return False
            if entry.entry_hash != entry._calculate_hash():
                return False
            expected_prev = entry.entry_hash
        return True

    def __ror__(self, other: Any) -> "ContinuityLedger":
        """Pipeline operator ingestion support: asset into my_ledger"""
        self.commit(other)
        return self

    def __call__(self, other: Any, alias: Optional[str] = None) -> "ContinuityLedger":
        """Callable pipeline operator support: asset |> my_ledger"""
        self.commit(other, alias=alias)
        return self


# Global Runtime Helpers injected into Haven namespaces
_GLOBAL_LEDGER = ContinuityLedger("default_system_ledger")

def checkpoint(asset: Any, alias: Optional[str] = None, ledger: Optional[ContinuityLedger] = None) -> LedgerEntry:
    target_ledger = ledger if ledger is not None else _GLOBAL_LEDGER
    return target_ledger.commit(asset, alias)

def verify_continuity(asset: Any, proof_or_hash: str) -> bool:
    if hasattr(asset, "odcs_hash"):
        res = (asset.odcs_hash() == proof_or_hash)
    else:
        res = (sha256_digest(asset) == proof_or_hash)
    if not res:
        raise AssertionError(f"Continuity verification failed for {asset}")
    return True
