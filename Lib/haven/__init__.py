"""
Haven Standard System Library v1.0.0
Copyright (c) 2026 Anirudha Puthraya.
"""

from .continuity import (
    DurableRecord,
    durable_record,
    LedgerEntry,
    ContinuityLedger,
    checkpoint,
    verify_continuity,
    _GLOBAL_LEDGER
)
from .merkle import MerkleTree
from .immutability import (
    ContinuityImmutabilityError,
    canonical_json_bytes,
    sha256_digest
)

__version__ = "1.0.0"
__author__ = "Anirudha Puthraya"
__all__ = [
    "DurableRecord",
    "durable_record",
    "LedgerEntry",
    "ContinuityLedger",
    "MerkleTree",
    "ContinuityImmutabilityError",
    "canonical_json_bytes",
    "sha256_digest",
    "checkpoint",
    "verify_continuity",
    "pipe_fn",
]

class pipe_fn:
    """Wraps regular functions to make them callable via pipeline transformations."""
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def __ror__(self, left):
        return self.fn(left)
