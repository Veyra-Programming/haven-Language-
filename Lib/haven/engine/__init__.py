"""
Ani++ / Haven OmniEngine Architecture
Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from .chrono import ChronoEngine, CausalityNode
from .reality import (
    RealityState,
    EntangledVariable,
    SynthesizedVariable,
    DurableVariable,
    entangled,
    synthesized,
    durable_var,
)
from .healer import AutonomousHealer, HealingReceipt, HealingStrategy, heal
from .cognitive import (
    CognitiveNode,
    CognitiveReactor,
    deterministic_embedding,
    cosine_similarity,
    euclidean_distance,
    dot_product,
    vector_magnitude,
    semantic_search,
)
from .runtime import OmniEngine, AniEngine, _GLOBAL_OMNI_ENGINE

__all__ = [
    # Master Engine
    "OmniEngine",
    "AniEngine",
    "_GLOBAL_OMNI_ENGINE",
    # 4D Chrono-Quantum Causality
    "ChronoEngine",
    "CausalityNode",
    # Polymorphic Reality & Entangled Memory
    "RealityState",
    "EntangledVariable",
    "SynthesizedVariable",
    "DurableVariable",
    "entangled",
    "synthesized",
    "durable_var",
    # Autonomous Self-Healing
    "AutonomousHealer",
    "HealingReceipt",
    "HealingStrategy",
    "heal",
    # AI-Symbiotic Cognitive Synthesis
    "CognitiveNode",
    "CognitiveReactor",
    "deterministic_embedding",
    "cosine_similarity",
    "euclidean_distance",
    "dot_product",
    "vector_magnitude",
    "semantic_search",
]
