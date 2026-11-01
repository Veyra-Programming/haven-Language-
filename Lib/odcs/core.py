"""
Open Digital Continuity Standard (ODCS) - Core Record & Immutability Engine.
Standard Specification by Anirudha Puthraya.
"""

from typing import Any, Dict, Optional, List, Type, TypeVar
import inspect
from .envelope import ContinuityAssetEnvelope, canonical_json, compute_sha256
from .merkle import MerkleTree

T = TypeVar("T")


from haven.immutability import ContinuityImmutabilityError


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

    def to_envelope(self, provenance_author: str = "Anirudha Puthraya", parent_hash: Optional[str] = None, **kwargs: Any) -> ContinuityAssetEnvelope:
        """Encapsulate this record into an ODCS Asset Envelope with Merkle proofs."""
        if self._odcs_envelope_cache and not parent_hash:
            return self._odcs_envelope_cache

        payload = self.odcs_dict()
        fields = [f"{k}:{v}" for k, v in sorted(payload.items())]
        merkle = MerkleTree(fields)

        env = ContinuityAssetEnvelope(
            asset_type=self.__class__.__name__,
            payload=payload,
            parent_hash=parent_hash,
            creator=provenance_author,
            merkle_root=merkle.root_hash,
            metadata=kwargs.get("metadata", {})
        )
        if not parent_hash:
            object.__setattr__(self, "_odcs_envelope_cache", env)
        return env

    def odcs_envelope(self, creator: str = "Anirudha Puthraya", parent_hash: Optional[str] = None, **kwargs: Any) -> ContinuityAssetEnvelope:
        """Alias for to_envelope matching ODCS specification terminology."""
        author = creator or kwargs.get("provenance_author", "Anirudha Puthraya")
        return self.to_envelope(provenance_author=author, parent_hash=parent_hash, **kwargs)

    def verify_field_proof(self, field_name: str, expected_root: str) -> bool:
        """Verify that a specific field is a cryptographically valid component of the Merkle root."""
        env = self.to_envelope()
        return env.verify(expected_root)

    def __repr__(self) -> str:
        fields = ", ".join(f"{k}={v!r}" for k, v in self.odcs_dict().items())
        return f"{self.__class__.__name__}({fields}) [ODCS Sealed]"


def durable_record(cls: Type[T]) -> Type[T]:
    """
    Class decorator transforming any Haven class into an ODCS DurableRecord.
    Used automatically by Haven's `durable record Name:` grammar construct.
    """
    if issubclass(cls, DurableRecord):
        return cls

    orig_init = cls.__init__
    has_custom_init = (orig_init is not object.__init__)

    def wrapped_init(self: Any, *args: Any, **kwargs: Any) -> None:
        if has_custom_init:
            sig = inspect.signature(orig_init)
            bound = sig.bind_partial(self, *args, **kwargs)
            bound.apply_defaults()
            for k, v in bound.arguments.items():
                if k != "self":
                    object.__setattr__(self, k, v)
            orig_init(self, *args, **kwargs)
        else:
            # Map args and kwargs to fields defined in annotations
            annotations = list(getattr(cls, "__annotations__", {}).keys())
            for idx, arg in enumerate(args):
                if idx < len(annotations):
                    object.__setattr__(self, annotations[idx], arg)
            for k, v in kwargs.items():
                object.__setattr__(self, k, v)
        object.__setattr__(self, "_odcs_sealed", True)

    new_dict = dict(cls.__dict__)
    new_dict["__init__"] = wrapped_init
    new_dict["_odcs_sealed"] = False

    # Create new type inheriting from DurableRecord and original class
    bases = (DurableRecord,) + tuple(b for b in cls.__bases__ if b is not object)
    decorated_cls = type(cls.__name__, bases, new_dict)
    return decorated_cls  # type: ignore
