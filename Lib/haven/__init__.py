"""
Haven Standard System Library v1.0.0
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
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
sha256 = sha256_digest
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

# Enterprise Annotations & Meta-Annotations
from .annotations import (
    RetentionPolicy,
    ElementType,
    Retention,
    Target,
    interface,
    Override,
    OverrideError,
    Deprecated,
    Synchronized,
    Volatile,
    Sealed,
    SealedHierarchyError,
    Serial,
    Durable,
    Transactional,
    TransactionRollback,
    Audit,
    ContinuityCheck,
    CircuitBreaker,
    Retry,
    get_annotations,
    has_annotation,
    get_annotation,
)

# Enterprise Java Concepts
from .enterprise import (
    Interface,
    default,
    implements,
    InterfaceImplementationError,
    SealedClass,
    HavenEnum,
    Record,
    TypeBound,
    GenericContainer,
)

# Concurrency & Reactive Primitives
from .concurrency import (
    CompletableFuture,
    AtomicInteger,
    AtomicBoolean,
    AtomicReference,
    CountDownLatch,
    ReentrantLock,
    VirtualExecutor,
)

# Open Financial Continuity Standard (OFCS)
import ofcs
from ofcs import (
    Money,
    Currency,
    CurrencyMismatchError,
    ExchangeRate,
    DoubleEntryRecord,
    FinancialAccount,
    OFCSFinancialLedger,
    UnbalancedTransactionError,
    InsufficientFundsError,
    DuplicateTransactionError,
    FinancialTransaction,
    Idempotent,
    ZeroDrift,
    ZeroDriftViolationError,
    ReconciliationEngine,
    ReconciliationReport,
    USD, EUR, GBP, INR, JPY, BTC, HVN
)

# Haven Backend & Microservices Framework
from .backend import (
    Response,
    HavenJSONEncoder,
    Request,
    RouteEntry,
    Router,
    Middleware,
    CORSMiddleware,
    ContinuityAuditMiddleware,
    RateLimiterMiddleware,
    HavenHTTPHandler,
    HavenServer,
    HavenApp,
    register_continuity_endpoints,
    TestClient,
    TestResponse,
    DurableModel,
    Field,
    APIKeyAuthMiddleware,
    BearerAuthMiddleware,
    require_auth,
    BackgroundTaskPool,
    mount_ofcs_vault,
)

# Universal Living Intent Fabric (ULIF)
from .intent import (
    FallbackPolicy,
    InvariantViolationError,
    LivingReceipt,
    IntentContract,
    LivingIntentRegistry,
    mint_living_receipt,
    execute_intent,
    living_intent,
)

# Universal Dimensional Safety Engine (UDE)
from .units import (
    Dimension,
    Unit,
    UnitQuantity,
    DimensionalSafetyError,
    meter,
    kilometer,
    second,
    millisecond,
    hour,
    kilogram,
    gram,
    byte,
    megabyte,
    gigabyte,
    meters_per_second,
    km_per_hour,
    megabytes_per_second,
    meters,
    kilometers,
    seconds,
    milliseconds,
    hours,
    kilograms,
    grams,
    megabytes,
    gigabytes,
    celsius,
    volts,
    units,
)

# Autonomous Living Agent Mesh (ALAM)
from .agents import (
    AgentMemoryEntry,
    AgentEpisodicLedger,
    LivingSwarm,
)

# Universal Global Natural Dialects Engine (UGND)
from .i18n import translate_dialects

# Zero-Knowledge & Post-Quantum Continuity (ZK-ODCS)
from .zk import (
    PedersenCommitment,
    ZKRangeProof,
    ZKVerificationError,
    commit_value,
    prove_range,
    verify_range_proof,
    QuantumResistantVault,
)

# Reactive Living Stream & Event Flow Engine (HavenFlow)
from .flow import (
    Flow,
    flow_of,
    flow_map,
    flow_filter,
    flow_window,
    flow_collect,
    EventStream,
)

# Autonomous Neural Reasoning & Thought Graphs (HavenNeural)
from .neural import (
    ThoughtNode,
    ThoughtGraph,
)

# Edge Hardware & IoT Telemetry Standard (HavenIoT)
from .iot import (
    SensorTelemetry,
    ActuatorController,
    EdgeAirgapSupervisor,
    ActuatorSafetyViolation,
)

# Ani++ OmniEngine Architecture (Chrono-Quantum Causality & Entangled Reality)
from .engine import (
    OmniEngine,
    AniEngine,
    _GLOBAL_OMNI_ENGINE,
    ChronoEngine,
    CausalityNode,
    RealityState,
    EntangledVariable,
    SynthesizedVariable,
    DurableVariable,
    entangled,
    synthesized,
    durable_var,
    AutonomousHealer,
    HealingReceipt,
    HealingStrategy,
    heal,
    CognitiveNode,
    CognitiveReactor,
    deterministic_embedding,
    cosine_similarity,
    euclidean_distance,
    dot_product,
    vector_magnitude,
    semantic_search,
)

# Industrial All-Field Superpowers: Scientific, Robotics & Cyber Defense
from .scientific import (
    Matrix,
    Series,
    DataFrame,
)
from .robotics import (
    PIDController,
    KalmanFilter,
    CircularRingBuffer,
)
from .cyber import (
    CyberVault,
    ByzantineConsensus,
    SandboxedProcess,
)

# Cryptography & Ciphers Suite
from .crypto import (
    RailFenceCipher,
    ColumnarTranspositionCipher,
    CaesarCipher,
    VigenereCipher,
    AtbashCipher,
    AffineCipher,
    PlayfairCipher,
    PolybiusSquare,
    FeistelCipher,
    DiffieHellman,
    ShamirSecretSharing,
    HavenContinuumCipher,
    rail_fence_encrypt,
    rail_fence_decrypt,
    caesar_encrypt,
    caesar_decrypt,
    vigenere_encrypt,
    vigenere_decrypt,
    atbash_cipher,
    affine_encrypt,
    affine_decrypt,
    playfair_encrypt,
    playfair_decrypt,
    polybius_encrypt,
    polybius_decrypt,
    columnar_encrypt,
    columnar_decrypt,
    feistel_encrypt,
    feistel_decrypt,
    continuum_seal,
    continuum_unseal,
    encrypt as cipher_encrypt,
    decrypt as cipher_decrypt,
)
import haven.crypto as crypto

AniApp = HavenApp
AniServer = HavenServer

# Haven 100+ Standard Methods Library
from .methods import *
from .methods import methods as haven_methods




__version__ = "3.0.0 (Ani++ / Haven)"
__status__ = "General Availability (GA)"
__author__ = "Anirudha Puthraya"
__brand__ = "Ani++ / Haven"
__standard__ = "Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)"

# Establish Haven System Identity
import sys
import types
try:
    sys.implementation = types.SimpleNamespace(
        name='ani++',
        cache_tag='ani-300',
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
    "sha256",
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
    # Enterprise Annotations
    "RetentionPolicy",
    "ElementType",
    "Retention",
    "Target",
    "interface",
    "Override",
    "OverrideError",
    "Deprecated",
    "Synchronized",
    "Volatile",
    "Sealed",
    "SealedHierarchyError",
    "Serial",
    "Durable",
    "Transactional",
    "TransactionRollback",
    "Audit",
    "ContinuityCheck",
    "CircuitBreaker",
    "Retry",
    "get_annotations",
    "has_annotation",
    "get_annotation",
    # Enterprise Java Concepts
    "Interface",
    "default",
    "implements",
    "InterfaceImplementationError",
    "SealedClass",
    "HavenEnum",
    "Record",
    "TypeBound",
    "GenericContainer",
    # Concurrency Primitives
    "CompletableFuture",
    "AtomicInteger",
    "AtomicBoolean",
    "AtomicReference",
    "CountDownLatch",
    "ReentrantLock",
    "VirtualExecutor",
    # Open Financial Continuity Standard (OFCS)
    "ofcs",
    "Money",
    "Currency",
    "CurrencyMismatchError",
    "ExchangeRate",
    "DoubleEntryRecord",
    "FinancialAccount",
    "OFCSFinancialLedger",
    "UnbalancedTransactionError",
    "InsufficientFundsError",
    "DuplicateTransactionError",
    "FinancialTransaction",
    "Idempotent",
    "ZeroDrift",
    "ZeroDriftViolationError",
    "ReconciliationEngine",
    "ReconciliationReport",
    "USD", "EUR", "GBP", "INR", "JPY", "BTC", "HVN",
    # Haven Backend Framework
    "Response",
    "HavenJSONEncoder",
    "Request",
    "RouteEntry",
    "Router",
    "Middleware",
    "CORSMiddleware",
    "ContinuityAuditMiddleware",
    "RateLimiterMiddleware",
    "HavenHTTPHandler",
    "HavenServer",
    "HavenApp",
    "register_continuity_endpoints",
    "TestClient",
    "TestResponse",
    "DurableModel",
    "Field",
    "APIKeyAuthMiddleware",
    "BearerAuthMiddleware",
    "require_auth",
    "BackgroundTaskPool",
    "mount_ofcs_vault",
    # Universal Living Intent Fabric (ULIF)
    "FallbackPolicy",
    "InvariantViolationError",
    "LivingReceipt",
    "IntentContract",
    "LivingIntentRegistry",
    "mint_living_receipt",
    "execute_intent",
    "living_intent",
    # Universal Dimensional Safety Engine (UDE)
    "Dimension",
    "Unit",
    "UnitQuantity",
    "DimensionalSafetyError",
    "meter",
    "kilometer",
    "second",
    "millisecond",
    "hour",
    "kilogram",
    "gram",
    "byte",
    "megabyte",
    "gigabyte",
    "meters_per_second",
    "km_per_hour",
    "megabytes_per_second",
    "meters",
    "kilometers",
    "seconds",
    "milliseconds",
    "hours",
    "kilograms",
    "grams",
    "megabytes",
    "gigabytes",
    "celsius",
    "volts",
    "units",
    # Autonomous Living Agent Mesh (ALAM)
    "AgentMemoryEntry",
    "AgentEpisodicLedger",
    "LivingSwarm",
    # Universal Global Natural Dialects Engine (UGND)
    "translate_dialects",
    # Zero-Knowledge & Post-Quantum Continuity (ZK-ODCS)
    "PedersenCommitment",
    "ZKRangeProof",
    "ZKVerificationError",
    "commit_value",
    "prove_range",
    "verify_range_proof",
    "QuantumResistantVault",
    # Reactive Living Stream & Event Flow (HavenFlow)
    "Flow",
    "flow_of",
    "flow_map",
    "flow_filter",
    "flow_window",
    "flow_collect",
    "EventStream",
    # Autonomous Neural Reasoning & Thought Graphs (HavenNeural)
    "ThoughtNode",
    "ThoughtGraph",
    # Edge Hardware & IoT Telemetry Standard (HavenIoT)
    "SensorTelemetry",
    "ActuatorController",
    "EdgeAirgapSupervisor",
    "ActuatorSafetyViolation",
    # Ani++ OmniEngine Architecture
    "OmniEngine",
    "AniEngine",
    "_GLOBAL_OMNI_ENGINE",
    "AniApp",
    "AniServer",
    "ChronoEngine",
    "CausalityNode",
    "RealityState",
    "EntangledVariable",
    "SynthesizedVariable",
    "DurableVariable",
    "entangled",
    "synthesized",
    "durable_var",
    "AutonomousHealer",
    "HealingReceipt",
    "HealingStrategy",
    "heal",
    "CognitiveNode",
    "CognitiveReactor",
    "deterministic_embedding",
    "cosine_similarity",
    "euclidean_distance",
    "dot_product",
    "vector_magnitude",
    "semantic_search",
    # Industrial All-Field Superpowers: Scientific Computing
    "Matrix",
    "Series",
    "DataFrame",
    # Industrial All-Field Superpowers: Robotics & Cyber-Physical
    "PIDController",
    "KalmanFilter",
    "CircularRingBuffer",
    # Industrial All-Field Superpowers: Cyber Defense & Consensus
    "CyberVault",
    "ByzantineConsensus",
    "SandboxedProcess",
    # Cryptography & Ciphers Suite
    "crypto",
    "RailFenceCipher",
    "ColumnarTranspositionCipher",
    "CaesarCipher",
    "VigenereCipher",
    "AtbashCipher",
    "AffineCipher",
    "PlayfairCipher",
    "PolybiusSquare",
    "FeistelCipher",
    "DiffieHellman",
    "ShamirSecretSharing",
    "HavenContinuumCipher",
    "rail_fence_encrypt",
    "rail_fence_decrypt",
    "caesar_encrypt",
    "caesar_decrypt",
    "vigenere_encrypt",
    "vigenere_decrypt",
    "atbash_cipher",
    "affine_encrypt",
    "affine_decrypt",
    "playfair_encrypt",
    "playfair_decrypt",
    "polybius_encrypt",
    "polybius_decrypt",
    "columnar_encrypt",
    "columnar_decrypt",
    "feistel_encrypt",
    "feistel_decrypt",
    "continuum_seal",
    "continuum_unseal",
    "cipher_encrypt",
    "cipher_decrypt",
]
