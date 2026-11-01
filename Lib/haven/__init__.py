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
from odcs.core import ContinuityIntegrityError
from .algorithm import (
    ContinuityAlgorithm,
    StateTransitionStep,
    StateContinuityAlgorithm,
    ConsensusContinuityAlgorithm,
    EventSourcingContinuityAlgorithm,
    ODCSApp,
)
from odcs.crdt import (
    VectorClock,
    LWWRegister,
    PNCounter,
    AWORSet,
    OutboxPipeline,
)
from odcs.mesh import (
    MeshNode,
    GossipMesh,
)
from odcs.telemetry import (
    ContinuityMode,
    EnvironmentalTelemetry,
    adaptive_policy,
)
from odcs.intent import (
    IntentReceipt,
    ZeroIntentLossManager,
)

__version__ = "1.0.0"
__author__ = "Anirudha Puthraya"
__standard__ = "Open Digital Continuity Standard (ODCS)"

# Establish Haven System Identity
import sys
import types
try:
    sys.implementation = types.SimpleNamespace(
        name='haven',
        cache_tag='haven-100',
        version=sys.version_info,
        hexversion=sys.hexversion,
        supports_isolated_interpreters=True
    )
except Exception:
    pass

class pipe_fn:
    """Wraps regular functions to make them callable via pipeline transformations."""
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def __ror__(self, left):
        return self.fn(left)

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__standard__",
    # Layer 1: Core Immutability & Ledger
    "DurableRecord",
    "durable_record",
    "LedgerEntry",
    "ContinuityLedger",
    "MerkleTree",
    "ContinuityImmutabilityError",
    "ContinuityIntegrityError",
    "canonical_json_bytes",
    "sha256_digest",
    "checkpoint",
    "verify_continuity",
    "pipe_fn",
    # Layer 2: Transport & CRDT Consensus
    "VectorClock",
    "LWWRegister",
    "PNCounter",
    "AWORSet",
    "OutboxPipeline",
    "MeshNode",
    "GossipMesh",
    # Layer 3: Runtime & Environmental Adaptation
    "ContinuityMode",
    "EnvironmentalTelemetry",
    "adaptive_policy",
    # Layer 4: Application & Continuity UX
    "IntentReceipt",
    "ZeroIntentLossManager",
    # Continuity Algorithms & App Framework
    "ContinuityAlgorithm",
    "StateTransitionStep",
    "StateContinuityAlgorithm",
    "ConsensusContinuityAlgorithm",
    "EventSourcingContinuityAlgorithm",
    "ODCSApp",
]
