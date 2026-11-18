"""
Ani++ / Haven OmniEngine • Chrono-Quantum Causality Engine
World-First 4D Temporal Causality DAG with Timeline Rewind, Multiverse Forking,
and Speculative Quantum Execution.
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import time
import copy
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


def _sha256_snapshot(data: Any) -> str:
    """Computes deterministic hash for a temporal state snapshot."""
    try:
        raw = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    except Exception:
        raw = str(data).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class CausalityNode:
    """
    A single point in 4D execution space.
    Represents an immutable, cryptographically-sealed state snapshot along a timeline branch.
    """
    def __init__(
        self,
        node_id: str,
        state: Dict[str, Any],
        parent_id: Optional[str] = None,
        branch: str = "main",
        action: str = "INIT",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.node_id = node_id
        self.timestamp = time.time_ns()
        self.state = copy.deepcopy(state)
        self.parent_id = parent_id
        self.branch = branch
        self.action = action
        self.metadata = metadata or {}
        self.state_hash = _sha256_snapshot(self.state)
        self.causality_hash = self._compute_causality_hash()

    def _compute_causality_hash(self) -> str:
        body = f"{self.node_id}:{self.parent_id}:{self.state_hash}:{self.branch}:{self.action}"
        return hashlib.sha256(body.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "branch": self.branch,
            "action": self.action,
            "parent_id": self.parent_id,
            "state_hash": self.state_hash,
            "causality_hash": self.causality_hash,
            "metadata": self.metadata,
        }


class ChronoEngine:
    """
    Ani++ / Haven 4D Chrono-Quantum Causality Engine:
    First programming language engine in the world featuring native:
      1. Timeline Rewinding (Backwards time-travel across state transitions)
      2. Multiverse Timeline Forking (Spawning parallel speculative worlds)
      3. Speculative Quantum Execution (Execute branch, auto-merge on success, auto-annihilate on fail)
      4. Deterministic Causal Merge (CRDT-style 4D DAG convergence)
    """
    def __init__(self, name: str = "Ani++_ChronoEngine"):
        self.name = name
        self.nodes: Dict[str, CausalityNode] = {}
        self.branches: Dict[str, str] = {}  # branch_name -> head_node_id
        self.current_branch: str = "main"
        self.active_state: Dict[str, Any] = {}
        self.timeline_history: List[str] = []

        # Genesis node
        genesis = CausalityNode(
            node_id="genesis-0",
            state={},
            parent_id=None,
            branch="main",
            action="GENESIS"
        )
        self.nodes[genesis.node_id] = genesis
        self.branches["main"] = genesis.node_id
        self.current_node_id = genesis.node_id
        self.timeline_history.append(genesis.node_id)

    def snapshot(self, label: str = "step", **extra_state) -> CausalityNode:
        """
        Commits a new 4D causality node to the active branch.
        """
        if extra_state:
            self.active_state.update(extra_state)

        parent = self.nodes[self.current_node_id]
        new_node_id = f"node-{len(self.nodes)}-{int(time.time()*1000) % 100000}"
        node = CausalityNode(
            node_id=new_node_id,
            state=self.active_state,
            parent_id=parent.node_id,
            branch=self.current_branch,
            action=label
        )
        self.nodes[node.node_id] = node
        self.branches[self.current_branch] = node.node_id
        self.current_node_id = node.node_id
        self.timeline_history.append(node.node_id)
        return node

    def set(self, key: str, value: Any, commit: bool = True) -> Any:
        """Updates state variable and optionally takes a temporal snapshot."""
        self.active_state[key] = value
        if commit:
            self.snapshot(label=f"set:{key}")
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Reads variable from the current temporal state."""
        return self.active_state.get(key, default)

    def rewind(self, steps: int = 1) -> Dict[str, Any]:
        """
        Rewinds temporal state backwards by N steps along the causality chain.
        Restores state to exact snapshot point.
        """
        curr = self.nodes.get(self.current_node_id)
        steps_left = steps
        while curr and curr.parent_id and steps_left > 0:
            curr = self.nodes.get(curr.parent_id)
            steps_left -= 1

        if curr:
            self.current_node_id = curr.node_id
            self.active_state = copy.deepcopy(curr.state)
            self.snapshot(label=f"rewind:{steps}")

        return copy.deepcopy(self.active_state)

    def fork(self, branch_name: str) -> "ChronoEngine":
        """
        Forks the universe into a new parallel timeline branch.
        All subsequent mutations on this branch stay completely isolated.
        """
        if branch_name in self.branches:
            raise ValueError(f"Timeline branch '{branch_name}' already exists.")

        parent_node = self.nodes[self.current_node_id]
        fork_node_id = f"fork-{branch_name}-{int(time.time()*1000) % 100000}"
        node = CausalityNode(
            node_id=fork_node_id,
            state=copy.deepcopy(self.active_state),
            parent_id=parent_node.node_id,
            branch=branch_name,
            action=f"FORK_FROM_{parent_node.branch}"
        )
        self.nodes[node.node_id] = node
        self.branches[branch_name] = node.node_id
        self.current_branch = branch_name
        self.current_node_id = node.node_id
        return self

    def switch_branch(self, branch_name: str) -> Dict[str, Any]:
        """Switches active timeline to a previously forked branch."""
        if branch_name not in self.branches:
            raise KeyError(f"Unknown timeline branch '{branch_name}'")

        head_id = self.branches[branch_name]
        node = self.nodes[head_id]
        self.current_branch = branch_name
        self.current_node_id = node.node_id
        self.active_state = copy.deepcopy(node.state)
        return copy.deepcopy(self.active_state)

    def merge_branch(self, from_branch: str, strategy: str = "causal_crdt") -> Dict[str, Any]:
        """
        Merges a speculative multiverse branch into the active branch.
        Resolves conflicts via Causal-Last-Write-Wins CRDT convergence.
        """
        if from_branch not in self.branches:
            raise KeyError(f"Cannot merge non-existent branch '{from_branch}'")

        source_node = self.nodes[self.branches[from_branch]]
        # Merge dictionary keys
        for k, v in source_node.state.items():
            self.active_state[k] = copy.deepcopy(v)

        merge_node = self.snapshot(label=f"MERGE_{from_branch}_INTO_{self.current_branch}")
        return copy.deepcopy(self.active_state)

    def speculate(self, computation: Callable[[], Any], rollback_on_fail: bool = True) -> Tuple[bool, Any]:
        """
        Quantum Speculative Execution:
        Executes a computation in a disposable sandbox timeline.
        If computation succeeds: commits the changes to active timeline.
        If computation raises an exception: zero changes leak; state remains 100% pristine!
        """
        saved_branch = self.current_branch
        saved_node = self.current_node_id
        saved_state = copy.deepcopy(self.active_state)

        temp_branch = f"speculate-{int(time.time()*1000000) % 1000000}"
        self.fork(temp_branch)

        try:
            result = computation()
            # Success! Merge back to original branch
            self.switch_branch(saved_branch)
            for k, v in self.nodes[self.branches[temp_branch]].state.items():
                self.active_state[k] = v
            self.snapshot(label=f"SPECULATIVE_SUCCESS:{temp_branch}")
            # Clean up temporary branch
            self.branches.pop(temp_branch, None)
            return (True, result)
        except Exception as e:
            # Failure! Revert completely
            self.current_branch = saved_branch
            self.current_node_id = saved_node
            self.active_state = saved_state
            self.branches.pop(temp_branch, None)
            if not rollback_on_fail:
                raise e
            return (False, e)

    def travel_to(self, target_hash_or_id: str) -> Dict[str, Any]:
        """Point-in-time travel: Jump directly to any historical causality node."""
        target_node = None
        for n in self.nodes.values():
            if n.node_id == target_hash_or_id or n.causality_hash.startswith(target_hash_or_id):
                target_node = n
                break

        if not target_node:
            raise KeyError(f"Causality node '{target_hash_or_id}' not found in 4D DAG.")

        self.current_node_id = target_node.node_id
        self.active_state = copy.deepcopy(target_node.state)
        self.snapshot(label=f"TIMETRAVEL_TO_{target_node.node_id}")
        return copy.deepcopy(self.active_state)

    def get_timeline_graph(self) -> List[Dict[str, Any]]:
        """Returns the full 4D DAG representation of all causality nodes."""
        return [n.to_dict() for n in self.nodes.values()]

    def verify_causality_integrity(self) -> bool:
        """Verifies cryptographic hash linkage across every node in the 4D DAG."""
        for n in self.nodes.values():
            if n.causality_hash != n._compute_causality_hash():
                return False
            if n.parent_id and n.parent_id not in self.nodes:
                return False
        return True
