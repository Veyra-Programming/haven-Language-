"""
Open Digital Continuity Standard (ODCS) - Tamper-Evident Continuity Ledger.
Standard Specification by Anirudha Puthraya.
"""

from typing import List, Dict, Any, Optional, Union
import os
import json
from datetime import datetime, timezone
from .envelope import ContinuityAssetEnvelope, canonical_json, compute_sha256
from .core import DurableRecord, ContinuityIntegrityError


class LedgerEntry:
    """An individual cryptographically-sealed entry in the Continuity Ledger."""
    def __init__(
        self,
        index: int,
        prev_hash: str,
        envelope: ContinuityAssetEnvelope,
        alias: Optional[str] = None,
        author: str = "Anirudha Puthraya",
        timestamp: Optional[str] = None,
        entry_hash: Optional[str] = None,
    ) -> None:
        self.index: int = index
        self.prev_hash: str = prev_hash
        self.envelope: ContinuityAssetEnvelope = envelope
        self.alias: Optional[str] = alias
        self.author: str = author
        self.timestamp: str = timestamp or datetime.now(timezone.utc).isoformat()
        computed = self._compute_hash()
        self.entry_hash: str = entry_hash if entry_hash is not None else computed

    def _compute_hash(self) -> str:
        body = {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "envelope_hash": self.envelope.envelope_hash,
            "alias": self.alias,
            "author": self.author,
            "timestamp": self.timestamp,
        }
        return f"sha256:{compute_sha256(canonical_json(body))}"

    def verify(self) -> bool:
        if not self.envelope.verify_integrity():
            return False
        return self._compute_hash() == self.entry_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
            "alias": self.alias,
            "author": self.author,
            "timestamp": self.timestamp,
            "envelope": self.envelope.to_dict(),
        }


class ContinuityLedger:
    """
    Append-only, tamper-evident cryptographic continuity journal.
    Maintains a verifiable lineage chain from Genesis to Head.
    """
    GENESIS_HASH: str = "sha256:0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, name: str = "Primary-Continuity-Ledger", author: str = "Anirudha Puthraya") -> None:
        self.name: str = name
        self.author: str = author
        self.entries: List[LedgerEntry] = []
        self.alias_map: Dict[str, LedgerEntry] = {}
        self._init_genesis()

    def __call__(self, asset: Any) -> LedgerEntry:
        """Enables piping assets directly into the ledger: asset |> ledger or asset into ledger"""
        return self.checkpoint(asset)

    def _init_genesis(self) -> None:
        genesis_env = ContinuityAssetEnvelope(
            asset_id="genesis-root",
            asset_type="GenesisContinuityBlock",
            payload={
                "message": "Open Digital Continuity Standard (ODCS) Genesis Initialized",
                "standard": "ODCS-1.0.0",
                "specification_author": self.author,
            },
            creator=self.author,
        )
        genesis_entry = LedgerEntry(
            index=0,
            prev_hash=self.GENESIS_HASH,
            envelope=genesis_env,
            alias="genesis",
            author=self.author,
        )
        self.entries.append(genesis_entry)
        self.alias_map["genesis"] = genesis_entry

    @property
    def head_hash(self) -> str:
        return self.entries[-1].entry_hash

    def checkpoint(
        self,
        asset: Union[DurableRecord, ContinuityAssetEnvelope, Dict[str, Any], Any],
        alias: Optional[str] = None
    ) -> LedgerEntry:
        """Commit an asset into the append-only ledger and return the sealed entry."""
        if isinstance(asset, ContinuityAssetEnvelope):
            envelope = asset
        elif hasattr(asset, "odcs_envelope"):
            envelope = asset.odcs_envelope(parent_hash=self.head_hash)
        elif isinstance(asset, dict):
            envelope = ContinuityAssetEnvelope(payload=asset, parent_hash=self.head_hash)
        else:
            payload = getattr(asset, "__dict__", {"value": str(asset)})
            envelope = ContinuityAssetEnvelope(payload=payload, parent_hash=self.head_hash)

        new_entry = LedgerEntry(
            index=len(self.entries),
            prev_hash=self.head_hash,
            envelope=envelope,
            alias=alias,
            author=self.author,
        )
        self.entries.append(new_entry)
        if alias:
            self.alias_map[alias] = new_entry
        return new_entry

    def verify_chain(self) -> bool:
        """Cryptographically verify the unbroken continuity of the ledger from genesis to head."""
        if not self.entries:
            return False

        for i in range(len(self.entries)):
            entry = self.entries[i]
            if not entry.verify():
                return False
            if i == 0:
                if entry.prev_hash != self.GENESIS_HASH:
                    return False
            else:
                prev_entry = self.entries[i - 1]
                if entry.prev_hash != prev_entry.entry_hash:
                    return False

        return True

    def export_journal(self, file_path: str) -> str:
        """Export the full continuity journal to an external JSON file for long-term archiving."""
        data = {
            "standard": "ODCS-1.0.0",
            "author": self.author,
            "ledger_name": self.name,
            "export_time": datetime.now(timezone.utc).isoformat(),
            "total_entries": len(self.entries),
            "head_hash": self.head_hash,
            "entries": [e.to_dict() for e in self.entries],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(canonical_json(data))
        return file_path

    @classmethod
    def replay_journal(cls, file_path: str) -> "ContinuityLedger":
        """Reconstruct and verify an ODCS Continuity Ledger from an archived journal."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        ledger = cls(name=data.get("ledger_name", "Replayed-Ledger"), author=data.get("author", "Anirudha Puthraya"))
        ledger.entries.clear()
        ledger.alias_map.clear()

        for e_dict in data.get("entries", []):
            env_dict = e_dict.get("envelope", {})
            env = ContinuityAssetEnvelope(
                asset_id=env_dict.get("asset_id"),
                asset_type=env_dict.get("asset_type", "GenericRecord"),
                payload=env_dict.get("payload", {}),
                parent_hash=env_dict.get("parent_hash"),
                creator=env_dict.get("creator", "Anirudha Puthraya"),
                merkle_root=env_dict.get("merkle_root"),
                timestamp=env_dict.get("timestamp"),
                envelope_hash=env_dict.get("envelope_hash"),
            )
            # Reconstruct entry preserving exact archived timestamp and hash
            entry = LedgerEntry(
                index=e_dict.get("index", 0),
                prev_hash=e_dict.get("prev_hash", ""),
                envelope=env,
                alias=e_dict.get("alias"),
                author=e_dict.get("author", "Anirudha Puthraya"),
                timestamp=e_dict.get("timestamp"),
                entry_hash=e_dict.get("entry_hash"),
            )
            ledger.entries.append(entry)
            if entry.alias:
                ledger.alias_map[entry.alias] = entry

        if not ledger.verify_chain():
            raise ContinuityIntegrityError("Corrupted or tampered ODCS journal: verification failed during replay.")

        return ledger


# Global default ledger singleton
_GLOBAL_DEFAULT_LEDGER: Optional[ContinuityLedger] = None


def get_default_ledger() -> ContinuityLedger:
    global _GLOBAL_DEFAULT_LEDGER
    if _GLOBAL_DEFAULT_LEDGER is None:
        _GLOBAL_DEFAULT_LEDGER = ContinuityLedger()
    return _GLOBAL_DEFAULT_LEDGER


def checkpoint(
    asset: Any,
    alias: Optional[str] = None,
    ledger: Optional[ContinuityLedger] = None
) -> LedgerEntry:
    """
    Built-in Haven ODCS checkpoint function.
    Invoked directly by the Haven `checkpoint <target> [as <alias>] [into <ledger>]` syntax.
    """
    target_ledger = ledger or get_default_ledger()
    return target_ledger.checkpoint(asset, alias=alias)


def verify_continuity(asset_or_proof: Any, expected_proof: Any) -> bool:
    """
    Built-in Haven ODCS verification function.
    Invoked directly by the Haven `verify <target> with <proof>` syntax.
    """
    # 1. If target is a DurableRecord or Envelope
    if hasattr(asset_or_proof, "odcs_hash"):
        target_hash = asset_or_proof.odcs_hash()
    elif hasattr(asset_or_proof, "envelope_hash"):
        target_hash = asset_or_proof.envelope_hash
    elif isinstance(asset_or_proof, str):
        target_hash = asset_or_proof
    else:
        target_hash = f"sha256:{compute_sha256(canonical_json(asset_or_proof))}"

    if isinstance(expected_proof, str):
        matches = (target_hash == expected_proof or target_hash.endswith(expected_proof) or expected_proof in target_hash)
        if not matches:
            raise ContinuityIntegrityError(f"Verification failed: expected proof '{expected_proof}', got '{target_hash}'.")
        return True

    # 2. If verifying a ledger entry
    if hasattr(expected_proof, "entry_hash"):
        matches = (target_hash == expected_proof.envelope.envelope_hash or target_hash == expected_proof.entry_hash)
        if not matches:
            raise ContinuityIntegrityError(f"Verification failed against ledger entry: {expected_proof.entry_hash}.")
        return True

    return True
