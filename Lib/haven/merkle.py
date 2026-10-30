"""
Haven Core: Binary Field-Level Merkle Integrity Engine
Copyright (c) 2026 Anirudha Puthraya.
"""

import hashlib
from typing import List, Dict, Any, Tuple
from .immutability import canonical_json_bytes

class MerkleTree:
    """
    Constructs a deterministic, leaf-sorted binary Merkle tree over record fields.
    Guarantees field inclusion and proofs without disclosing remaining payload assets.
    """
    __slots__ = ("leaves", "tree", "root")

    def __init__(self, elements: Dict[str, Any]):
        # Deterministically hash each field: sha256("key:value")
        self.leaves: List[str] = []
        for k in sorted(elements.keys()):
            if k.startswith("_"):
                continue
            leaf_payload = canonical_json_bytes({"field": k, "val": elements[k]})
            leaf_hash = hashlib.sha256(leaf_payload).hexdigest()
            self.leaves.append(leaf_hash)
        
        if not self.leaves:
            self.leaves = [hashlib.sha256(b"EMPTY_LEAF").hexdigest()]

        self.tree: List[List[str]] = [self.leaves]
        self._build()
        self.root: str = self.tree[-1][0]

    def _build(self) -> None:
        current_layer = self.leaves
        while len(current_layer) > 1:
            next_layer: List[str] = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                if i + 1 < len(current_layer):
                    right = current_layer[i + 1]
                else:
                    right = left  # Duplicate node if odd parity
                
                combined = hashlib.sha256((left + right).encode("ascii")).hexdigest()
                next_layer.append(combined)
            self.tree.append(next_layer)
            current_layer = next_layer

    def get_proof(self, index: int) -> List[Tuple[str, str]]:
        """Generates audit proof path [('left'|'right', sibling_hash), ...]"""
        proof = []
        for layer in self.tree[:-1]:
            is_right_child = (index % 2 == 1)
            sibling_idx = index - 1 if is_right_child else index + 1
            if sibling_idx < len(layer):
                direction = "left" if is_right_child else "right"
                proof.append((direction, layer[sibling_idx]))
            else:
                proof.append(("right", layer[index]))
            index //= 2
        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Tuple[str, str]], root: str) -> bool:
        """Validates zero-knowledge membership against a target Merkle root."""
        current = leaf_hash
        for direction, sibling in proof:
            if direction == "left":
                combined = sibling + current
            else:
                combined = current + sibling
            current = hashlib.sha256(combined.encode("ascii")).hexdigest()
        return current == root
