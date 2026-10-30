"""
Open Digital Continuity Standard (ODCS) - Core Record & Immutability Engine.
Standard Specification by Anirudha Puthraya.
"""

from typing import Any, Dict, Optional, List, Type, TypeVar
import inspect
from .envelope import ContinuityAssetEnvelope, canonical_json, compute_sha256
from .merkle import MerkleTree

T = TypeVar("T")


class ContinuityImmutabilityError(Exception):
    """Raised when an attempt is made to mutate a sealed durable record."""
    pass


class ContinuityIntegrityError(Exception):
    """Raised when an asset or proof fails cryptographic verification."""
    pass


class DurableRecord:
    """
    Base class for all ODCS Digital Continuity Records.
    Guarantees:
      - Field immutability after construction
      - Deterministic canonical hashing
      - Built-in Merkle root computation over state fields
      - Automatic envelope generation and provenance lineage
    """
    _odcs_sealed: bool = False
    _odcs_envelope_cache: Optional[ContinuityAssetEnvelope] = None

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)
        self._odcs_seal()

    def _odcs_seal(self) -> None:
        """Lock the record from any future in-place modifications."""
        object.__setattr__(self, "_odcs_sealed", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_odcs_sealed", False):
            raise ContinuityImmutabilityError(
                f"ODCS Violation: Cannot modify attribute '{name}' on sealed DurableRecord '{self.__class__.__name__}'."
            )
        object.__setattr__(self, name, value)

    def odcs_dict(self) -> Dict[str, Any]:
        """Return dict of all non-private fields."""
        data = {}
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                data[k] = getattr(v, "odcs_dict", lambda: v)()
        return data

    def odcs_hash(self) -> str:
        """Compute the deterministic SHA-256 digest of this record."""
        return f"sha256:{compute_sha256(canonical_json(self.odcs_dict()))}"

    def odcs_merkle_tree(self) -> MerkleTree:
        """Build a Merkle tree of this record's sorted key-value pairs."""
        items = sorted(self.odcs_dict().items())
        return MerkleTree(items)

    def odcs_envelope(self, parent_hash: Optional[str] = None, creator: Optional[str] = None) -> ContinuityAssetEnvelope:
        """Generate a certified ContinuityAssetEnvelope for this record."""
        tree = self.odcs_merkle_tree()
        env = ContinuityAssetEnvelope(
            asset_type=self.__class__.__name__,
            payload=self.odcs_dict(),
            parent_hash=parent_hash,
            creator=creator or "Anirudha Puthraya / Haven ODCS Runtime",
            merkle_root=tree.root,
        )
        object.__setattr__(self, "_odcs_envelope_cache", env)
        return env

    def verify_integrity(self) -> bool:
        """Verify the integrity of this record's internal Merkle root and envelope."""
        env = getattr(self, "_odcs_envelope_cache", None) or self.odcs_envelope()
        return env.verify_integrity()

    def checkpoint(self, alias: Optional[str] = None, ledger: Optional[Any] = None) -> Any:
        """Checkpoint this record into a continuity ledger."""
        from .ledger import get_default_ledger
        target_ledger = ledger or get_default_ledger()
        return target_ledger.checkpoint(self, alias=alias)

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.odcs_dict().items())
        return f"{self.__class__.__name__}({attrs})"


def durable_record(cls: Type[T]) -> Type[T]:
    """
    Class decorator transforming any Python/Haven class into an ODCS DurableRecord.
    Used automatically by Haven's `durable record Name:` grammar construct.
    """
    if issubclass(cls, DurableRecord):
        return cls

    # Dynamically inject DurableRecord base and functionality
    orig_init = cls.__init__

    def wrapped_init(self: Any, *args: Any, **kwargs: Any) -> None:
        # If user passed positional args, map them to signature params
        sig = inspect.signature(orig_init)
        bound = sig.bind_partial(self, *args, **kwargs)
        bound.apply_defaults()
        for k, v in bound.arguments.items():
            if k != "self":
                object.__setattr__(self, k, v)
        orig_init(self, *args, **kwargs)
        object.__setattr__(self, "_odcs_sealed", True)

    new_dict = dict(cls.__dict__)
    new_dict["__init__"] = wrapped_init
    new_dict["_odcs_sealed"] = False

    # Create new type inheriting from DurableRecord and original class
    bases = (DurableRecord,) + tuple(b for b in cls.__bases__ if b is not object)
    decorated_cls = type(cls.__name__, bases, new_dict)
    return decorated_cls  # type: ignore
