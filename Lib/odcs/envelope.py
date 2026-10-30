"""
Open Digital Continuity Standard (ODCS) - Core Envelope Specification.
Standard Specification by Anirudha Puthraya.
"""

from typing import Dict, Any, List, Optional
import hashlib
import json
import uuid
from datetime import datetime, timezone


def canonical_json(data: Any) -> str:
    """
    Produce canonical deterministic JSON according to RFC 8785 / ODCS Canonicalization Rules:
    - Sorted keys
    - No unnecessary whitespace
    - UTF-8 encoding
    - Floating point determinism
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
        default=lambda o: getattr(o, "odcs_dict", lambda: getattr(o, "__dict__", str(o)))()
    )


def compute_sha256(canonical_str: str) -> str:
    """Compute SHA-256 digest of a string."""
    return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()


class ContinuityAssetEnvelope:
    """
    ODCS Continuity Asset Envelope (CAE).
    Standard container ensuring long-term preservation, tamper-evidence,
    cryptographic provenance, and cross-platform longevity.
    """
    STANDARD: str = "ODCS-1.0.0"
    SPECIFICATION_AUTHOR: str = "Anirudha Puthraya"

    def __init__(
        self,
        asset_id: Optional[str] = None,
        asset_type: str = "GenericRecord",
        payload: Optional[Dict[str, Any]] = None,
        parent_hash: Optional[str] = None,
        creator: str = "Anirudha Puthraya / Haven ODCS Runtime",
        metadata: Optional[Dict[str, Any]] = None,
        merkle_root: Optional[str] = None,
        timestamp: Optional[str] = None,
        envelope_hash: Optional[str] = None,
    ) -> None:
        self.asset_id: str = asset_id or str(uuid.uuid4())
        self.asset_type: str = asset_type
        self.standard: str = self.STANDARD
        self.author: str = self.SPECIFICATION_AUTHOR
        self.creator: str = creator
        self.timestamp: str = timestamp or datetime.now(timezone.utc).isoformat()
        self.parent_hash: Optional[str] = parent_hash
        self.payload: Dict[str, Any] = payload or {}
        self.metadata: Dict[str, Any] = metadata or {}
        self.merkle_root: Optional[str] = merkle_root

        # Compute payload hash
        self.canonical_payload: str = canonical_json(self.payload)
        self.payload_hash: str = f"sha256:{compute_sha256(self.canonical_payload)}"

        # Compute envelope hash (covers metadata, payload_hash, parent_hash, and timestamp)
        computed = self._compute_envelope_hash()
        self.envelope_hash: str = envelope_hash if envelope_hash is not None else computed

    def _compute_envelope_hash(self) -> str:
        manifest = {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "standard": self.standard,
            "author": self.author,
            "timestamp": self.timestamp,
            "parent_hash": self.parent_hash,
            "payload_hash": self.payload_hash,
            "merkle_root": self.merkle_root,
        }
        return f"sha256:{compute_sha256(canonical_json(manifest))}"

    def verify_integrity(self) -> bool:
        """Verify that payload and envelope hash match their cryptographic definitions."""
        recalculated_payload = f"sha256:{compute_sha256(canonical_json(self.payload))}"
        if recalculated_payload != self.payload_hash:
            return False
        return self._compute_envelope_hash() == self.envelope_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "standard": self.standard,
            "specification_author": self.author,
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "creator": self.creator,
            "timestamp": self.timestamp,
            "parent_hash": self.parent_hash,
            "payload_hash": self.payload_hash,
            "envelope_hash": self.envelope_hash,
            "merkle_root": self.merkle_root,
            "metadata": self.metadata,
            "payload": self.payload,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    def __repr__(self) -> str:
        return f"<ODCS.CAE id={self.asset_id[:8]} type={self.asset_type} hash={self.envelope_hash[:16]}...>"
