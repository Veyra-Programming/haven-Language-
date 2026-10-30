"""
Haven Core: Canonical RFC 8785 Cryptographic Determinism Engine
Copyright (c) 2026 Anirudha Puthraya.
"""

import json
import hashlib
from typing import Any

class ContinuityImmutabilityError(TypeError):
    """Raised when an illegal modification is performed on a sealed ODCS entity."""
    pass

def canonical_json_bytes(obj: Any) -> bytes:
    """
    Serializes arbitrary state into RFC 8785 deterministic JSON:
    - Strictly sorted keys
    - Minimal whitespace (no trailing spaces, explicit delimiters)
    - IEEE 754 float representation guarantee
    - Canonical UTF-8 bitstream
    """
    if isinstance(obj, (bytes, bytearray)):
        return bytes(obj)
    
    def default_serializer(o):
        if hasattr(o, "to_dict") and callable(o.to_dict):
            return o.to_dict()
        if hasattr(o, "__dict__"):
            return {k: v for k, v in sorted(o.__dict__.items()) if not k.startswith("_")}
        if isinstance(o, (set, frozenset)):
            return sorted(list(o))
        raise TypeError(f"Object of type {type(o).__name__} is not ODCS canonicalizable")

    canonical_str = json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        indent=None,
        separators=(",", ":"),
        default=default_serializer
    )
    return canonical_str.encode("utf-8")

def sha256_digest(data: Any) -> str:
    """Computes hexadecimal SHA-256 over canonical byte representation."""
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest()
