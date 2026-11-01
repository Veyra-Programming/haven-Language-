"""
Open Digital Continuity Standard (ODCS) SDK for Haven Programming Language.
Standard Specification and Architecture by Anirudha Puthraya.

Implements the 4-Layer ODCS Framework:
  - Layer 1: Local Durability & Cryptographic Storage (DurableRecord, Ledger, MerkleTree)
  - Layer 2: Transport, Synchronization & Consensus (VectorClock, CRDTs: PNCounter, LWWRegister, AWORSet, OutboxPipeline)
  - Layer 3: Runtime & Environmental Adaptation (ContinuityMode, EnvironmentalTelemetry, adaptive_policy)
  - Layer 4: Application & Continuity UX (IntentReceipt, ZeroIntentLossManager)
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
from .algorithm import (
    ContinuityAlgorithm,
    StateTransitionStep,
    StateContinuityAlgorithm,
    ConsensusContinuityAlgorithm,
    EventSourcingContinuityAlgorithm,
    ODCSApp,
)
from .crdt import (
    VectorClock,
    LWWRegister,
    PNCounter,
    AWORSet,
    OutboxPipeline,
)
from .mesh import (
    MeshNode,
    GossipMesh,
)
from .telemetry import (
    ContinuityMode,
    EnvironmentalTelemetry,
    adaptive_policy,
)
from .intent import (
    IntentReceipt,
    ZeroIntentLossManager,
)

__version__ = "1.0.0"
__author__ = "Anirudha Puthraya"
__standard__ = "Open Digital Continuity Standard (ODCS)"

# Install ODCS primitives into builtins so all Haven programs can use them out-of-the-box
builtins.durable_record = durable_record
builtins.checkpoint = checkpoint
builtins.verify_continuity = verify_continuity
builtins.ODCSApp = ODCSApp
builtins.ContinuityAlgorithm = ContinuityAlgorithm
builtins.StateContinuityAlgorithm = StateContinuityAlgorithm
builtins.ContinuityLedger = ContinuityLedger
# Layer 2 CRDTs & Mesh
builtins.VectorClock = VectorClock
builtins.LWWRegister = LWWRegister
builtins.PNCounter = PNCounter
builtins.AWORSet = AWORSet
builtins.MeshNode = MeshNode
builtins.GossipMesh = GossipMesh
# Layer 3 Adaptation
builtins.ContinuityMode = ContinuityMode
builtins.EnvironmentalTelemetry = EnvironmentalTelemetry
builtins.adaptive_policy = adaptive_policy
# Layer 4 Zero Intent Loss
builtins.IntentReceipt = IntentReceipt
builtins.ZeroIntentLossManager = ZeroIntentLossManager

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__standard__",
    # Layer 1: Core Immutability & Storage
    "DurableRecord",
    "durable_record",
    "ContinuityImmutabilityError",
    "ContinuityIntegrityError",
    "ContinuityAssetEnvelope",
    "canonical_json",
    "compute_sha256",
    "MerkleTree",
    "ContinuityLedger",
    "LedgerEntry",
    "checkpoint",
    "verify_continuity",
    "get_default_ledger",
    "ContinuitySchema",
    "SchemaMigrationError",
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
