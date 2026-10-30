"""
Open Digital Continuity Standard (ODCS) SDK for Haven Programming Language.
Standard Specification and Architecture by Anirudha Puthraya.
"""

import builtins

from .envelope import ContinuityAssetEnvelope, canonical_json, compute_sha256
from .merkle import MerkleTree
from .core import (
    DurableRecord,
    durable_record,
    ContinuityImmutabilityError,
    ContinuityIntegrityError,
)
from .ledger import (
    ContinuityLedger,
    LedgerEntry,
    checkpoint,
    verify_continuity,
    get_default_ledger,
)
from .schema import ContinuitySchema, SchemaMigrationError

__version__ = "1.0.0"
__author__ = "Anirudha Puthraya"
__standard__ = "Open Digital Continuity Standard (ODCS)"

# Install ODCS primitives into builtins so all Haven programs can use them out-of-the-box
builtins.durable_record = durable_record
builtins.checkpoint = checkpoint
builtins.verify_continuity = verify_continuity

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__standard__",
    # Core Immutability
    "DurableRecord",
    "durable_record",
    "ContinuityImmutabilityError",
    "ContinuityIntegrityError",
    # Envelope & Provenance
    "ContinuityAssetEnvelope",
    "canonical_json",
    "compute_sha256",
    "MerkleTree",
    # Ledger & Checkpointing
    "ContinuityLedger",
    "LedgerEntry",
    "checkpoint",
    "verify_continuity",
    "get_default_ledger",
    # Schema Evolution
    "ContinuitySchema",
    "SchemaMigrationError",
]
