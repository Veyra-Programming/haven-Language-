"""
Ani++ Programming Language (Dual-Identity with Haven)
The Sovereign Digital Continuity & Quantum-Causality All-Rounder Language
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

# Re-export all Haven runtime symbols under the Ani++ brand
import haven
from haven import *
from haven.engine import (
    OmniEngine,
    AniEngine,
    ChronoEngine,
    CausalityNode,
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
    CognitiveReactor,
    semantic_search,
    cosine_similarity,
    deterministic_embedding,
)
from haven.scientific import (
    Matrix,
    Series,
    DataFrame,
)
from haven.robotics import (
    PIDController,
    KalmanFilter,
    CircularRingBuffer,
)
from haven.cyber import (
    CyberVault,
    ByzantineConsensus,
    SandboxedProcess,
)
from haven.crypto import (
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
import haven.quantum as quantum
import haven.ai as ai
import haven.net as net
import haven.signal as signal
import haven.geo as geo

from haven.quantum import (
    QuantumCircuit,
    QuantumState,
    circuit as quantum_circuit,
)
from haven.ai import (
    Value,
    Neuron,
    Layer,
    MLP,
    Adam,
    mse_loss,
    BpeTokenizer,
    KMeans,
)
from haven.net import (
    MicroApp,
    Request,
    Response,
    RateLimiter,
    TestClient,
    sse_event,
)
from haven.signal import (
    dft,
    idft,
    fft,
    spectrum_magnitude,
    sine_wave,
    square_wave,
    sawtooth_wave,
    triangle_wave,
    lowpass_filter,
    encode_wav,
)
from haven.geo import (
    haversine_distance,
    initial_bearing,
    destination_point,
    geohash_encode,
    geohash_decode,
    point_in_polygon,
    BoundingBox,
)

__version__ = "3.0.0 (Ani++ / Haven Dual Edition)"
__author__ = "Anirudha Puthraya"
__brand__ = "Ani++ / Haven"

# Aliases for Ani++
AniApp = haven.backend.HavenApp
AniServer = haven.backend.HavenServer
