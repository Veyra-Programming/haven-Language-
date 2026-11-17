"""
Haven Autonomous Neural Reasoning & Thought Graph Engine (HavenNeural)
Standard: Open Digital Continuity Standard (ODCS) Cognitive Logic Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides verifiable reasoning graphs, hypothesis branching, confidence-weighted
decision paths, and automated invalid-branch pruning for autonomous AI systems.
"""

import uuid
import hashlib
from typing import Dict, List, Any, Optional

from .merkle import MerkleTree


class ThoughtNode:
    """A discrete unit of cognitive reasoning in an agent's decision graph."""
    def __init__(
        self,
        node_id: str,
        content: str,
        confidence: float = 1.0,
        parent_id: Optional[str] = None
    ):
        self.node_id = node_id
        self.content = content
        self.confidence = max(0.0, min(1.0, float(confidence)))
        self.parent_id = parent_id
        self.children_ids: List[str] = []
        self.validated: Optional[bool] = None  # None = pending, True = confirmed, False = rejected

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "content": self.content,
            "confidence": self.confidence,
            "parent_id": self.parent_id,
            "validated": self.validated,
            "children": list(self.children_ids)
        }

    def __repr__(self) -> str:
        status = "PENDING" if self.validated is None else ("VALID" if self.validated else "REJECTED")
        return f"<ThoughtNode [{status} {self.confidence:.2f}] {self.content[:35]}...>"


class ThoughtGraph:
    """
    Directed Acyclic Graph (DAG) representing an agent's reasoning trace.
    Allows branching alternative paths, validating evidence, and pruning dead ends.
    """
    def __init__(self, objective: str):
        self.objective = objective
        self.nodes: Dict[str, ThoughtNode] = {}
        self.root_id: Optional[str] = None

    def add_root(self, hypothesis: str, confidence: float = 1.0) -> ThoughtNode:
        node_id = f"thought-root-{uuid.uuid4().hex[:6]}"
        node = ThoughtNode(node_id=node_id, content=hypothesis, confidence=confidence)
        self.nodes[node_id] = node
        self.root_id = node_id
        return node

    def branch(self, parent_id: str, thought: str, confidence: float = 1.0) -> ThoughtNode:
        if parent_id not in self.nodes:
            raise KeyError(f"Parent thought node '{parent_id}' not found in graph.")
        node_id = f"thought-step-{uuid.uuid4().hex[:6]}"
        node = ThoughtNode(node_id=node_id, content=thought, confidence=confidence, parent_id=parent_id)
        self.nodes[node_id] = node
        self.nodes[parent_id].children_ids.append(node_id)
        return node

    def validate(self, node_id: str, is_valid: bool) -> None:
        """Sets the validation status of a node."""
        if node_id in self.nodes:
            self.nodes[node_id].validated = is_valid

    def prune_invalid_branches(self) -> int:
        """
        Recursively identifies and removes any node whose ancestor or self was marked invalid.
        Returns the count of pruned nodes.
        """
        pruned_count = 0

        def _collect_descendants(nid: str, accum: set) -> None:
            accum.add(nid)
            for cid in self.nodes.get(nid, ThoughtNode("", "")).children_ids:
                _collect_descendants(cid, accum)

        to_remove = set()
        for nid, node in list(self.nodes.items()):
            if node.validated is False:
                _collect_descendants(nid, to_remove)

        for rid in to_remove:
            if rid in self.nodes:
                # Remove from parent's children
                parent_id = self.nodes[rid].parent_id
                if parent_id and parent_id in self.nodes:
                    if rid in self.nodes[parent_id].children_ids:
                        self.nodes[parent_id].children_ids.remove(rid)
                del self.nodes[rid]
                pruned_count += 1

        return pruned_count

    def get_best_reasoning_path(self) -> List[ThoughtNode]:
        """
        Finds the highest cumulative confidence path from root to a valid leaf.
        """
        if not self.root_id or self.root_id not in self.nodes:
            return []

        best_path: List[ThoughtNode] = []
        best_score = -1.0

        def _dfs(current: ThoughtNode, current_path: List[ThoughtNode], current_score: float) -> None:
            nonlocal best_path, best_score
            new_path = current_path + [current]
            new_score = current_score * current.confidence

            # If leaf node or no more valid children
            valid_children = [
                self.nodes[cid] for cid in current.children_ids
                if cid in self.nodes and self.nodes[cid].validated is not False
            ]

            if not valid_children:
                if new_score > best_score:
                    best_score = new_score
                    best_path = new_path
                return

            for child in valid_children:
                _dfs(child, new_path, new_score)

        root = self.nodes[self.root_id]
        if root.validated is not False:
            _dfs(root, [], 1.0)

        return best_path

    def compute_merkle_digest(self) -> str:
        """Computes a Merkle root hash representing the entire verified graph."""
        if not self.nodes:
            return hashlib.sha256(b"empty_thought_graph").hexdigest()
        elements = {
            nid: f"{n.content}:{n.confidence}:{n.validated}"
            for nid, n in self.nodes.items()
        }
        tree = MerkleTree(elements)
        return tree.root
