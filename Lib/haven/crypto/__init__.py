"""
Ani++ / Haven Cryptography & Cipher Super-Package
Comprehensive Suite: Classical Transposition & Substitution, Modern Feistel & Diffie-Hellman,
and the World-First Haven Continuum Cipher (CQE-512).
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from .classical import (
    RailFenceCipher,
    ColumnarTranspositionCipher,
    CaesarCipher,
    VigenereCipher,
    AtbashCipher,
    AffineCipher,
    PlayfairCipher,
    PolybiusSquare,
)

from .modern import (
    FeistelCipher,
    DiffieHellman,
    ShamirSecretSharing,
)

from .invented import (
    HavenContinuumCipher,
)

# Friendly Top-Level Functional Helpers
def rail_fence_encrypt(text: str, rails: int = 3) -> str:
    """Encrypts text using Rail Fence (zig-zag) transposition."""
    return RailFenceCipher.encrypt(text, rails)

def rail_fence_decrypt(ciphertext: str, rails: int = 3) -> str:
    """Decrypts ciphertext using Rail Fence (zig-zag) transposition."""
    return RailFenceCipher.decrypt(ciphertext, rails)

def caesar_encrypt(text: str, shift: int = 3) -> str:
    """Encrypts text using Caesar shift cipher."""
    return CaesarCipher.encrypt(text, shift)

def caesar_decrypt(ciphertext: str, shift: int = 3) -> str:
    """Decrypts ciphertext using Caesar shift cipher."""
    return CaesarCipher.decrypt(ciphertext, shift)

def vigenere_encrypt(text: str, key: str) -> str:
    """Encrypts text using polyalphabetic Vigenère cipher."""
    return VigenereCipher.encrypt(text, key)

def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """Decrypts ciphertext using polyalphabetic Vigenère cipher."""
    return VigenereCipher.decrypt(ciphertext, key)

def atbash_cipher(text: str) -> str:
    """Symmetric alphabet inversion cipher (A <-> Z)."""
    return AtbashCipher.encrypt(text)

def affine_encrypt(text: str, a: int = 5, b: int = 8) -> str:
    """Encrypts text using Affine cipher E(x) = (ax + b) mod 26."""
    return AffineCipher.encrypt(text, a, b)

def affine_decrypt(ciphertext: str, a: int = 5, b: int = 8) -> str:
    """Decrypts ciphertext using Affine cipher."""
    return AffineCipher.decrypt(ciphertext, a, b)

def playfair_encrypt(text: str, key: str) -> str:
    """Encrypts text using Playfair 5x5 digraph matrix cipher."""
    return PlayfairCipher.encrypt(text, key)

def playfair_decrypt(ciphertext: str, key: str) -> str:
    """Decrypts ciphertext using Playfair 5x5 digraph matrix cipher."""
    return PlayfairCipher.decrypt(ciphertext, key)

def polybius_encrypt(text: str) -> str:
    """Encrypts text into Polybius square numeric coordinates."""
    return PolybiusSquare.encrypt(text)

def polybius_decrypt(ciphertext: str) -> str:
    """Decrypts Polybius square numeric coordinates into text."""
    return PolybiusSquare.decrypt(ciphertext)

def columnar_encrypt(text: str, key: str) -> str:
    """Encrypts text using Keyed Columnar Transposition."""
    return ColumnarTranspositionCipher.encrypt(text, key)

def columnar_decrypt(ciphertext: str, key: str) -> str:
    """Decrypts ciphertext using Keyed Columnar Transposition."""
    return ColumnarTranspositionCipher.decrypt(ciphertext, key)

def feistel_encrypt(text: str, key: str, rounds: int = 16) -> bytes:
    """Encrypts text using 16-round symmetric Feistel block cipher."""
    return FeistelCipher(key, rounds=rounds).encrypt(text)

def feistel_decrypt(ciphertext: bytes, key: str, rounds: int = 16) -> str:
    """Decrypts ciphertext using 16-round symmetric Feistel block cipher."""
    return FeistelCipher(key, rounds=rounds).decrypt(ciphertext)

def continuum_seal(text: str, key: str, epoch: int = None, context: str = "haven:continuum") -> dict:
    """Seals text using the world-first Haven Continuum Cipher (CQE-512)."""
    return HavenContinuumCipher.seal(text, key, epoch=epoch, context=context)

def continuum_unseal(envelope: dict, key: str, context: str = "haven:continuum") -> str:
    """Unseals and decrypts a Haven Continuum Cipher (CQE-512) envelope."""
    return HavenContinuumCipher.unseal_text(envelope, key, expected_context=context)


# Universal Dispatcher Interface
def encrypt(algorithm: str, text: str, key: any = None, **kwargs) -> any:
    """Universal encryption dispatcher for all supported Haven ciphers."""
    algo = algorithm.lower().replace("-", "_").replace(" ", "_")
    if algo in ("rail_fence", "railfence", "zigzag"):
        rails = int(key if key is not None else kwargs.get("rails", 3))
        return rail_fence_encrypt(text, rails)
    elif algo in ("caesar", "rot"):
        shift = int(key if key is not None else kwargs.get("shift", 3))
        return caesar_encrypt(text, shift)
    elif algo in ("vigenere", "polyalphabetic"):
        return vigenere_encrypt(text, str(key))
    elif algo in ("playfair", "digraph"):
        return playfair_encrypt(text, str(key))
    elif algo in ("atbash", "invert"):
        return atbash_cipher(text)
    elif algo in ("affine",):
        a = kwargs.get("a", 5)
        b = kwargs.get("b", 8)
        return affine_encrypt(text, a, b)
    elif algo in ("polybius", "square"):
        return polybius_encrypt(text)
    elif algo in ("columnar", "columnar_transposition"):
        return columnar_encrypt(text, str(key))
    elif algo in ("feistel", "block"):
        return feistel_encrypt(text, str(key), rounds=kwargs.get("rounds", 16))
    elif algo in ("continuum", "cqe_512", "chrono_quantum", "haven"):
        return continuum_seal(text, str(key), epoch=kwargs.get("epoch"), context=kwargs.get("context", "haven:continuum"))
    else:
        raise ValueError(f"Unknown encryption algorithm: '{algorithm}'. Supported: rail_fence, caesar, vigenere, playfair, atbash, affine, polybius, columnar, feistel, continuum.")


def decrypt(algorithm: str, ciphertext: any, key: any = None, **kwargs) -> any:
    """Universal decryption dispatcher for all supported Haven ciphers."""
    algo = algorithm.lower().replace("-", "_").replace(" ", "_")
    if algo in ("rail_fence", "railfence", "zigzag"):
        rails = int(key if key is not None else kwargs.get("rails", 3))
        return rail_fence_decrypt(ciphertext, rails)
    elif algo in ("caesar", "rot"):
        shift = int(key if key is not None else kwargs.get("shift", 3))
        return caesar_decrypt(ciphertext, shift)
    elif algo in ("vigenere", "polyalphabetic"):
        return vigenere_decrypt(ciphertext, str(key))
    elif algo in ("playfair", "digraph"):
        return playfair_decrypt(ciphertext, str(key))
    elif algo in ("atbash", "invert"):
        return atbash_cipher(ciphertext)
    elif algo in ("affine",):
        a = kwargs.get("a", 5)
        b = kwargs.get("b", 8)
        return affine_decrypt(ciphertext, a, b)
    elif algo in ("polybius", "square"):
        return polybius_decrypt(ciphertext)
    elif algo in ("columnar", "columnar_transposition"):
        return columnar_decrypt(ciphertext, str(key))
    elif algo in ("feistel", "block"):
        return feistel_decrypt(ciphertext, str(key), rounds=kwargs.get("rounds", 16))
    elif algo in ("continuum", "cqe_512", "chrono_quantum", "haven"):
        return continuum_unseal(ciphertext, str(key), context=kwargs.get("context", "haven:continuum"))
    else:
        raise ValueError(f"Unknown decryption algorithm: '{algorithm}'. Supported: rail_fence, caesar, vigenere, playfair, atbash, affine, polybius, columnar, feistel, continuum.")


__all__ = [
    # Ciphers & Algorithms
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
    # Functions
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
    "encrypt",
    "decrypt",
]
