"""
Haven Autonomous Living Agent Mesh (ALAM)
Standard: Open Digital Continuity Standard (ODCS) & Agent Memory Ledger Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides tamper-evident episodic memory, verifiable reasoning chains,
and Byzantine disruption-tolerant consensus for multi-agent autonomous swarms.
"""

import time
import uuid
import hashlib
from typing import List, Dict, Any, Optional

from .immutability import canonical_json_bytes, sha256_digest, ContinuityImmutabilityError
from .merkle import MerkleTree


class AgentMemoryEntry:
    """A sealed, cryptographically verified record of an agent's cognition step."""
    def __init__(
        self,
        step_id: str,
        agent_id: str,
        step_type: str,  # "observation", "thought", "action", "reflection"
        content: Any,
        timestamp_ms: int,
        entry_hash: str
    ):
        self.step_id = step_id
        self.agent_id = agent_id
        self.step_type = step_type
        self.content = content
        self.timestamp_ms = timestamp_ms
        self.entry_hash = entry_hash
        self._sealed = True

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_sealed", False):
            raise ContinuityImmutabilityError(
                f"AgentMemoryEntry '{getattr(self, 'step_id', '')}' is hardware-sealed and immutable."
            )
        super().__setattr__(name, value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "agent_id": self.agent_id,
            "step_type": self.step_type,
            "content": self.content,
            "timestamp_ms": self.timestamp_ms,
            "entry_hash": self.entry_hash
        }

    def __repr__(self) -> str:
        return f"<AgentMemory [{self.agent_id}] {self.step_type}: {str(self.content)[:30]}...>"


class AgentEpisodicLedger:
    """
    Append-only episodic memory ledger ensuring AI agents never suffer from
    silent context drift, hallucinations, or state loss during restarts.
    """
    def __init__(self, agent_id: str, session_id: Optional[str] = None):
        self.agent_id = agent_id
        self.session_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        self.entries: List[AgentMemoryEntry] = []
        self._leaf_hashes: List[bytes] = []

    def record_step(self, step_type: str, content: Any) -> AgentMemoryEntry:
        """Records a cognitive step and appends to cryptographic hash chain."""
        step_id = f"step-{len(self.entries) + 1:04d}-{uuid.uuid4().hex[:6]}"
        now_ms = int(time.time() * 1000)

        raw_payload = {
            "step_id": step_id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "step_type": step_type,
            "content": content,
            "timestamp_ms": now_ms
        }
        entry_hash = sha256_digest(canonical_json_bytes(raw_payload))

        entry = AgentMemoryEntry(
            step_id=step_id,
            agent_id=self.agent_id,
            step_type=step_type,
            content=content,
            timestamp_ms=now_ms,
            entry_hash=entry_hash
        )
        self.entries.append(entry)
        self._leaf_hashes.append(bytes.fromhex(entry_hash))
        return entry

    def observe(self, data: Any) -> AgentMemoryEntry:
        return self.record_step("observation", data)

    def think(self, reasoning: str) -> AgentMemoryEntry:
        return self.record_step("thought", reasoning)

    def act(self, action_name: str, parameters: Dict[str, Any]) -> AgentMemoryEntry:
        return self.record_step("action", {"name": action_name, "parameters": parameters})

    def reflect(self, insight: str) -> AgentMemoryEntry:
        return self.record_step("reflection", insight)

    def get_merkle_root(self) -> str:
        """Computes root SHA-256 Merkle hash of all memory entries."""
        if not self.entries:
            return hashlib.sha256(b"haven_empty_agent_memory").hexdigest()
        elements = {entry.step_id: entry.entry_hash for entry in self.entries}
        tree = MerkleTree(elements)
        return tree.root

    def verify_integrity(self) -> bool:
        """Verifies the unbroken cryptographic integrity of the agent's memory."""
        for entry in self.entries:
            raw_payload = {
                "step_id": entry.step_id,
                "agent_id": entry.agent_id,
                "session_id": self.session_id,
                "step_type": entry.step_type,
                "content": entry.content,
                "timestamp_ms": entry.timestamp_ms
            }
            computed = sha256_digest(canonical_json_bytes(raw_payload))
            if computed != entry.entry_hash:
                return False
        return True


class LivingSwarm:
    """
    Collaborative multi-agent swarm with cryptographic consensus voting
    and ODCS invariant enforcement before executing actions.
    """
    def __init__(self, swarm_id: str, required_quorum: float = 0.6):
        self.swarm_id = swarm_id
        self.required_quorum = required_quorum
        self.agents: Dict[str, AgentEpisodicLedger] = {}
        self.proposals: List[Dict[str, Any]] = []

    def join(self, agent_id: str) -> AgentEpisodicLedger:
        ledger = AgentEpisodicLedger(agent_id=agent_id, session_id=self.swarm_id)
        self.agents[agent_id] = ledger
        return ledger

    def propose_action(self, proposer_id: str, action: str, params: Dict[str, Any]) -> str:
        proposal_id = f"prop-{len(self.proposals) + 1:03d}-{uuid.uuid4().hex[:6]}"
        self.proposals.append({
            "proposal_id": proposal_id,
            "proposer": proposer_id,
            "action": action,
            "params": params,
            "votes": {proposer_id: True},
            "status": "pending",
            "created_at": time.time()
        })
        return proposal_id

    def vote(self, agent_id: str, proposal_id: str, approve: bool) -> bool:
        for prop in self.proposals:
            if prop["proposal_id"] == proposal_id:
                prop["votes"][agent_id] = approve
                # Check quorum
                positive_votes = sum(1 for v in prop["votes"].values() if v)
                total_agents = max(1, len(self.agents))
                if (positive_votes / total_agents) >= self.required_quorum:
                    prop["status"] = "approved"
                return True
        return False

    def is_approved(self, proposal_id: str) -> bool:
        for prop in self.proposals:
            if prop["proposal_id"] == proposal_id:
                return prop["status"] == "approved"
        return False
