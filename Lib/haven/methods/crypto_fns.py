"""
Haven Standard Library - Cryptographic, Hashing & Security Methods
Standard: Open Digital Continuity Standard (ODCS) & Sovereign Security Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import hashlib
import hmac
import secrets
import uuid
import time
import os
from typing import Union

BytesOrStr = Union[str, bytes]


def _to_bytes(data: BytesOrStr) -> bytes:
    if isinstance(data, str):
        return data.encode("utf-8")
    return data


def sha256_hex(data: BytesOrStr) -> str:
    """Computes SHA-256 hexadecimal hash."""
    return hashlib.sha256(_to_bytes(data)).hexdigest()


def sha512_hex(data: BytesOrStr) -> str:
    """Computes SHA-512 hexadecimal hash."""
    return hashlib.sha512(_to_bytes(data)).hexdigest()


def sha3_256_hex(data: BytesOrStr) -> str:
    """Computes SHA3-256 post-quantum compatible hash."""
    return hashlib.sha3_256(_to_bytes(data)).hexdigest()


def sha3_512_hex(data: BytesOrStr) -> str:
    """Computes SHA3-512 hash."""
    return hashlib.sha3_512(_to_bytes(data)).hexdigest()


def blake2b_hex(data: BytesOrStr) -> str:
    """Computes high-speed BLAKE2b hash."""
    return hashlib.blake2b(_to_bytes(data)).hexdigest()


def md5_hex(data: BytesOrStr) -> str:
    """Computes legacy MD5 hash (for non-security checksums)."""
    return hashlib.md5(_to_bytes(data)).hexdigest()


def hmac_sha256_hex(key: BytesOrStr, data: BytesOrStr) -> str:
    """Computes HMAC-SHA256 signature."""
    return hmac.new(_to_bytes(key), _to_bytes(data), hashlib.sha256).hexdigest()


def hmac_sha512_hex(key: BytesOrStr, data: BytesOrStr) -> str:
    """Computes HMAC-SHA512 signature."""
    return hmac.new(_to_bytes(key), _to_bytes(data), hashlib.sha512).hexdigest()


def pbkdf2_hash_hex(password: BytesOrStr, salt: BytesOrStr, iterations: int = 100_000) -> str:
    """Derives a key using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        'sha256',
        _to_bytes(password),
        _to_bytes(salt),
        iterations
    ).hex()


def constant_time_compare(val1: str, val2: str) -> bool:
    """Compares two strings in constant time to prevent timing attacks."""
    return hmac.compare_digest(val1, val2)


def random_bytes_sec(n: int) -> bytes:
    """Generates n cryptographically secure random bytes."""
    return secrets.token_bytes(n)


def random_hex_sec(n_bytes: int = 16) -> str:
    """Generates cryptographically secure random hex string."""
    return secrets.token_hex(n_bytes)


def random_token_sec(length: int = 32) -> str:
    """Generates cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(length)[:length]


def random_int_sec(min_v: int, max_v: int) -> int:
    """Generates cryptographically secure random integer in [min_v, max_v]."""
    return secrets.randbelow(max_v - min_v + 1) + min_v


def generate_uuid4_str() -> str:
    """Generates standard UUIDv4 random identifier string."""
    return str(uuid.uuid4())


def generate_uuid7_str() -> str:
    """
    Generates time-ordered UUIDv7 string with millisecond monotonic precision.
    """
    now_ms = int(time.time() * 1000)
    rand_bytes = secrets.token_bytes(10)
    time_high = (now_ms >> 16) & 0xFFFFFFFF
    time_mid = now_ms & 0xFFFF

    # Construct standard 128-bit layout
    b = bytearray(16)
    b[0:4] = time_high.to_bytes(4, 'big')
    b[4:6] = time_mid.to_bytes(2, 'big')
    b[6] = 0x70 | (rand_bytes[0] & 0x0F)  # Version 7
    b[7] = rand_bytes[1]
    b[8] = 0x80 | (rand_bytes[2] & 0x3F)  # RFC 4122 Variant
    b[9:16] = rand_bytes[3:10]

    return str(uuid.UUID(bytes=bytes(b)))


def keccak_digest(data: BytesOrStr) -> str:
    """Computes Keccak-256 digest simulation."""
    return hashlib.sha3_256(_to_bytes(data)).hexdigest()


def hash_file_sha256(path: str) -> str:
    """Computes SHA-256 checksum of an entire file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def mask_hash(data: BytesOrStr, prefix_chars: int = 8) -> str:
    """Computes SHA-256 and formats as prefix...suffix for concise logging."""
    full = sha256_hex(data)
    return f"{full[:prefix_chars]}...{full[-prefix_chars:]}"


def derive_hkdf(salt: BytesOrStr, ikm: BytesOrStr, info: BytesOrStr = b"", length: int = 32) -> bytes:
    """Extract and Expand HKDF key derivation."""
    prk = hmac.new(_to_bytes(salt), _to_bytes(ikm), hashlib.sha256).digest()
    okm = hmac.new(prk, _to_bytes(info) + b"\x01", hashlib.sha256).digest()
    return okm[:length]
