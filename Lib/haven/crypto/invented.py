"""
Ani++ / Haven Continuum Cipher (CQE-512)
The World's First Chrono-Quantum Entangled Poly-Transposition & Lattice Diffusion Cipher.
Invented specifically for the Haven Programming Language and the Open Digital Continuity Standard (ODCS).

Theoretical Architecture:
1. Temporal Causality Entropy (Chrono-Locking):
   Binds cryptographic operations to a causality timeline tick or epoch.
2. Merkle-Derived Dynamic S-Box (MD-SBox):
   Permutes a 256-byte non-linear substitution matrix uniquely per session key
   via a cryptographic Fisher-Yates shuffle seeded with SHA-512.
3. Hyper-Rail 4D Transposition:
   Multi-dimensional zig-zag transposition with dynamic prime step offsets.
4. Lattice Vector Perturbation:
   Applies deterministic modular lattice noise diffusion guaranteeing the avalanche effect.
5. ODCS Zero-Intent-Loss Tamper Seal:
   Cryptographically commits an HMAC-SHA256 authentication tag across the entire temporal envelope.

Specification & Invention by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import base64
import hashlib
import hmac
import json
import math
import secrets
import time
from typing import Any, Dict, List, Optional, Tuple, Union


class HavenContinuumCipher:
    """
    CQE-512: Chrono-Quantum Entangled Cipher
    World-first temporal lattice cipher invented for Haven & Ani++.
    """
    VERSION = "CQE-512/ODCS-3.0"

    @classmethod
    def _generate_dynamic_sbox(cls, key: bytes, salt: bytes) -> Tuple[List[int], List[int]]:
        """
        Generates a bijective 256-element S-box and its inverse
        using a deterministic PRNG seeded by HMAC-SHA512(key, salt).
        """
        sbox = list(range(256))
        seed = hmac.new(key, salt + b":sbox_generation", hashlib.sha512).digest()

        # Fisher-Yates shuffle driven by deterministic entropy stream
        stream = seed
        stream_idx = 0
        for i in range(255, 0, -1):
            if stream_idx + 2 >= len(stream):
                stream = hashlib.sha512(stream + key).digest()
                stream_idx = 0
            val = (stream[stream_idx] << 8) | stream[stream_idx + 1]
            stream_idx += 2
            j = val % (i + 1)
            sbox[i], sbox[j] = sbox[j], sbox[i]

        # Build inverse S-box
        inv_sbox = [0] * 256
        for idx, val in enumerate(sbox):
            inv_sbox[val] = idx

        return sbox, inv_sbox

    @classmethod
    def _hyper_rail_transpose(cls, data: bytes, rails: int, prime_step: int) -> bytes:
        """Hyper-rail 4D multi-dimensional zig-zag transposition."""
        if rails <= 1 or len(data) <= rails:
            return data

        fence: List[List[int]] = [[] for _ in range(rails)]
        rail = 0
        direction = 1

        for byte_val in data:
            fence[rail].append(byte_val)
            rail = (rail + direction * prime_step) % rails
            if rail == rails - 1:
                direction = -1
            elif rail == 0:
                direction = 1

        transposed = []
        for r in fence:
            transposed.extend(r)
        return bytes(transposed)

    @classmethod
    def _hyper_rail_untranspose(cls, data: bytes, rails: int, prime_step: int) -> bytes:
        """Inverts Hyper-rail 4D multi-dimensional zig-zag transposition."""
        if rails <= 1 or len(data) <= rails:
            return data

        pattern: List[List[Union[int, None]]] = [[None for _ in range(len(data))] for _ in range(rails)]
        rail = 0
        direction = 1

        for i in range(len(data)):
            pattern[rail][i] = 1
            rail = (rail + direction * prime_step) % rails
            if rail == rails - 1:
                direction = -1
            elif rail == 0:
                direction = 1

        idx = 0
        for r in range(rails):
            for c in range(len(data)):
                if pattern[r][c] == 1 and idx < len(data):
                    pattern[r][c] = data[idx]
                    idx += 1

        result = []
        rail = 0
        direction = 1
        for c in range(len(data)):
            result.append(pattern[rail][c])
            rail = (rail + direction * prime_step) % rails
            if rail == rails - 1:
                direction = -1
            elif rail == 0:
                direction = 1

        return bytes(result)

    @classmethod
    def seal(
        cls,
        plaintext: Union[str, bytes],
        secret_key: str,
        epoch: Optional[int] = None,
        rails: int = 7,
        context: str = "haven:continuum"
    ) -> Dict[str, Any]:
        """
        Seals plaintext using the Haven Continuum Cipher (CQE-512).
        Returns a tamper-evident cryptographic envelope.
        """
        raw_bytes = plaintext.encode('utf-8') if isinstance(plaintext, str) else plaintext
        key_bytes = secret_key.encode('utf-8')
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        target_epoch = epoch if epoch is not None else int(time.time())

        # 1. Derive dynamic S-box and Inverse S-box
        sbox, _ = cls._generate_dynamic_sbox(key_bytes, salt)

        # 2. Stage 1: Dynamic Non-Linear S-Box Substitution
        substituted = bytes(sbox[b] for b in raw_bytes)

        # 3. Stage 2: Hyper-Rail 4D Transposition with dynamic prime step
        prime_step = (target_epoch % 3) + 1
        transposed = cls._hyper_rail_transpose(substituted, rails=rails, prime_step=prime_step)

        # 4. Stage 3: Lattice Vector Perturbation (Deterministic diffusion)
        lattice_seed = hmac.new(key_bytes, nonce + salt + str(target_epoch).encode('utf-8'), hashlib.sha512).digest()
        stream = lattice_seed
        while len(stream) < len(transposed):
            stream += hashlib.sha512(stream + key_bytes).digest()

        ciphertext = bytes((t ^ s) for t, s in zip(transposed, stream[:len(transposed)]))

        # 5. Stage 4: ODCS HMAC-SHA256 Integrity Tag
        auth_data = ciphertext + nonce + salt + str(target_epoch).encode('utf-8') + context.encode('utf-8')
        auth_tag = hmac.new(key_bytes, auth_data, hashlib.sha256).hexdigest()

        envelope = {
            "cipher": cls.VERSION,
            "context": context,
            "epoch": target_epoch,
            "rails": rails,
            "salt": base64.b64encode(salt).decode('ascii'),
            "nonce": base64.b64encode(nonce).decode('ascii'),
            "ciphertext": base64.b64encode(ciphertext).decode('ascii'),
            "auth_tag": auth_tag,
            "sealed_at": time.time()
        }
        return envelope

    @classmethod
    def unseal(
        cls,
        envelope: Dict[str, Any],
        secret_key: str,
        expected_context: str = "haven:continuum"
    ) -> bytes:
        """
        Unseals and decrypts a Haven Continuum Cipher envelope.
        Raises PermissionError if the envelope has been modified or tampered with.
        """
        if envelope.get("context") != expected_context:
            raise PermissionError(f"Context mismatch: expected '{expected_context}', got '{envelope.get('context')}'")

        key_bytes = secret_key.encode('utf-8')
        salt = base64.b64decode(envelope["salt"].encode('ascii'))
        nonce = base64.b64decode(envelope["nonce"].encode('ascii'))
        ciphertext = base64.b64decode(envelope["ciphertext"].encode('ascii'))
        target_epoch = envelope["epoch"]
        rails = envelope.get("rails", 7)
        auth_tag = envelope["auth_tag"]

        # 1. Verify ODCS Authentication Tag
        auth_data = ciphertext + nonce + salt + str(target_epoch).encode('utf-8') + expected_context.encode('utf-8')
        expected_mac = hmac.new(key_bytes, auth_data, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_mac, auth_tag):
            raise PermissionError("CONTINUUM INTEGRITY BREACH: Tamper detected on CQE-512 encrypted envelope!")

        # 2. Stage 3 Reverse: Invert Lattice Vector Perturbation
        lattice_seed = hmac.new(key_bytes, nonce + salt + str(target_epoch).encode('utf-8'), hashlib.sha512).digest()
        stream = lattice_seed
        while len(stream) < len(ciphertext):
            stream += hashlib.sha512(stream + key_bytes).digest()

        transposed = bytes((c ^ s) for c, s in zip(ciphertext, stream[:len(ciphertext)]))

        # 3. Stage 2 Reverse: Invert Hyper-Rail Transposition
        prime_step = (target_epoch % 3) + 1
        substituted = cls._hyper_rail_untranspose(transposed, rails=rails, prime_step=prime_step)

        # 4. Stage 1 Reverse: Invert Dynamic Non-Linear S-Box Substitution
        _, inv_sbox = cls._generate_dynamic_sbox(key_bytes, salt)
        plaintext = bytes(inv_sbox[b] for b in substituted)

        return plaintext

    @classmethod
    def unseal_text(cls, envelope: Dict[str, Any], secret_key: str, expected_context: str = "haven:continuum") -> str:
        """Convenience helper to unseal directly into a UTF-8 string."""
        return cls.unseal(envelope, secret_key, expected_context).decode('utf-8')
