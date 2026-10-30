"""
Open Digital Continuity Standard (ODCS) - Merkle Provenance Tree.
Standard Specification by Anirudha Puthraya.
"""

from typing import List, Optional, Tuple, Dict, Any
import hashlib
from .envelope import canonical_json


def hash_leaf(data: Any) -> str:
    """Hash a leaf value into a 32-byte hex string."""
    encoded = canonical_json(data).encode('utf-8')
    return hashlib.sha256(b"\x00" + encoded).hexdigest()


def hash_nodes(left: str, right: str) -> str:
    """Hash two child hashes together with a 0x01 domain separator."""
    combined = left.encode('utf-8') + right.encode('utf-8')
    return hashlib.sha256(b"\x01" + combined).hexdigest()


class MerkleTree:
    """
    Binary Merkle Tree for tamper-evident data structure proofs under ODCS.
    Enables zero-knowledge field verification and asset integrity auditing.
    """
    def __init__(self, elements: List[Any]) -> None:
        self.elements: List[Any] = elements
        self.leaves: List[str] = [hash_leaf(e) for e in elements]
        if not self.leaves:
            self.leaves = [hash_leaf("")]
        self.levels: List[List[str]] = [self.leaves]
        self._build_tree()

    def _build_tree(self) -> None:
        current = self.leaves
        while len(current) > 1:
            next_level: List[str] = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                next_level.append(hash_nodes(left, right))
            self.levels.append(next_level)
            current = next_level

    @property
    def root(self) -> str:
        """The cryptographic root hash of the Merkle Tree."""
        return self.levels[-1][0]

    def get_proof(self, index: int) -> List[Tuple[str, str]]:
        """
        Generate Merkle audit path for the element at index.
        Returns list of (sibling_hash, direction) where direction is 'left' or 'right'.
        """
        if index < 0 or index >= len(self.elements):
            raise IndexError("Element index out of bounds for Merkle proof.")

        proof: List[Tuple[str, str]] = []
        curr_idx = index
        for level in self.levels[:-1]:
            is_right = curr_idx % 2 == 1
            sibling_idx = curr_idx - 1 if is_right else curr_idx + 1
            if sibling_idx < len(level):
                sibling_hash = level[sibling_idx]
            else:
                sibling_hash = level[curr_idx]  # duplicate self for odd length

            proof.append((sibling_hash, 'left' if is_right else 'right'))
            curr_idx //= 2

        return proof

    @staticmethod
    def verify_proof(leaf_data: Any, proof: List[Tuple[str, str]], expected_root: str) -> bool:
        """Verify that leaf_data is part of the Merkle Tree with expected_root."""
        curr_hash = hash_leaf(leaf_data)
        for sibling_hash, direction in proof:
            if direction == 'left':
                curr_hash = hash_nodes(sibling_hash, curr_hash)
            else:
                curr_hash = hash_nodes(curr_hash, sibling_hash)
        return curr_hash == expected_root
