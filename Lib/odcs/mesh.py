"""
Open Digital Continuity Standard (ODCS) - Layer 2 P2P Mesh & Gossip Replication
Standard Specification & Architecture by Anirudha Puthraya.

Implements multi-node partitioned network topologies, asynchronous delta gossip,
causality frontier tracking via Vector Clocks, and CRDT state convergence
under extreme network dropouts, high-latency satellite, and airgapped conditions.
"""

from typing import Dict, List, Set, Tuple, Any, Optional
import time
from .core import ContinuityIntegrityError
from .crdt import VectorClock, PNCounter, AWORSet, LWWRegister, OutboxPipeline
from .ledger import ContinuityLedger, LedgerEntry


class MeshNode:
    """
    Represents an autonomous ODCS node operating with local Layer 1 storage,
    causality tracking, outbox staging, and CRDT state stores.
    """

    def __init__(self, node_id: str, name: Optional[str] = None):
        self.node_id = str(node_id)
        self.name = name or f"Node-{self.node_id}"
        self.clock = VectorClock({self.node_id: 0})
        self.outbox = OutboxPipeline(max_batch_size=50)
        self.ledger = ContinuityLedger(name=f"Ledger-{self.node_id}")

        # CRDT State Stores
        self.counters: Dict[str, PNCounter] = {}
        self.sets: Dict[str, AWORSet] = {}
        self.registers: Dict[str, LWWRegister] = {}

    def get_counter(self, name: str) -> PNCounter:
        if name not in self.counters:
            self.counters[name] = PNCounter(node_id=self.node_id)
        return self.counters[name]

    def get_set(self, name: str) -> AWORSet:
        if name not in self.sets:
            self.sets[name] = AWORSet()
        return self.sets[name]

    def get_register(self, name: str, default: Any = None) -> LWWRegister:
        if name not in self.registers:
            self.registers[name] = LWWRegister(value=default, node_id=self.node_id)
        return self.registers[name]

    def mutate_counter(self, name: str, delta: int) -> int:
        """Applies a local counter mutation, stages to outbox, and records to ledger."""
        cnt = self.get_counter(name)
        if delta >= 0:
            cnt.inc(delta)
        else:
            cnt.dec(-delta)

        self.clock.increment(self.node_id)
        payload = {
            "type": "crdt_counter",
            "name": name,
            "delta": delta,
            "state": cnt.to_dict(),
            "clock": self.clock.to_dict(),
        }
        self.outbox.stage(payload)
        self.ledger.append(payload, alias=f"counter_{name}_{delta:+d}")
        return cnt.value

    def mutate_set_add(self, name: str, item: Any) -> Set[Any]:
        """Adds an item to a distributed set, stages to outbox, and records to ledger."""
        s = self.get_set(name)
        s.add(item)
        self.clock.increment(self.node_id)
        payload = {
            "type": "crdt_set_add",
            "name": name,
            "item": item,
            "state": s.to_dict(),
            "clock": self.clock.to_dict(),
        }
        self.outbox.stage(payload)
        self.ledger.append(payload, alias=f"set_add_{name}_{item}")
        return s.elements

    def mutate_set_remove(self, name: str, item: Any) -> Set[Any]:
        """Removes an item from a distributed set, stages to outbox, and records to ledger."""
        s = self.get_set(name)
        s.remove(item)
        self.clock.increment(self.node_id)
        payload = {
            "type": "crdt_set_remove",
            "name": name,
            "item": item,
            "state": s.to_dict(),
            "clock": self.clock.to_dict(),
        }
        self.outbox.stage(payload)
        self.ledger.append(payload, alias=f"set_rem_{name}_{item}")
        return s.elements

    def mutate_register(self, name: str, val: Any) -> Any:
        """Sets an LWW register, stages to outbox, and records to ledger."""
        reg = self.get_register(name)
        reg.set(val)
        self.clock.increment(self.node_id)
        payload = {
            "type": "crdt_register_set",
            "name": name,
            "val": val,
            "state": reg.to_dict(),
            "clock": self.clock.to_dict(),
        }
        self.outbox.stage(payload)
        self.ledger.append(payload, alias=f"reg_set_{name}")
        return reg.value

    def produce_sync_delta(self) -> Dict[str, Any]:
        """Pulls unacknowledged mutations to transmit across Layer 2."""
        mutations = self.outbox.pull_batch()
        return {
            "from_node": self.node_id,
            "clock": self.clock.to_dict(),
            "mutations": mutations,
            "counters": {k: v.to_dict() for k, v in self.counters.items()},
            "sets": {k: v.to_dict() for k, v in self.sets.items()},
            "registers": {k: v.to_dict() for k, v in self.registers.items()},
        }

    def receive_sync_delta(self, delta: Dict[str, Any]) -> List[str]:
        """
        Receives an inbound sync delta from a peer. Merges causality clock,
        converges CRDTs, and returns list of processed mutation IDs for ACK.
        """
        remote_clock = VectorClock(delta.get("clock", {}))
        self.clock = self.clock.merge(remote_clock)

        # Merge Counters
        for name, cnt_data in delta.get("counters", {}).items():
            local_cnt = self.get_counter(name)
            remote_cnt = PNCounter.from_dict(cnt_data)
            self.counters[name] = local_cnt.merge(remote_cnt)

        # Merge Sets
        for name, set_data in delta.get("sets", {}).items():
            local_set = self.get_set(name)
            remote_set = AWORSet.from_dict(set_data)
            self.sets[name] = local_set.merge(remote_set)

        # Merge Registers
        for name, reg_data in delta.get("registers", {}).items():
            local_reg = self.get_register(name)
            remote_reg = LWWRegister.from_dict(reg_data)
            self.registers[name] = local_reg.merge(remote_reg)

        processed_ids = [m["mutation_id"] for m in delta.get("mutations", []) if "mutation_id" in m]
        return processed_ids

    def acknowledge_remote(self, processed_ids: List[str]) -> None:
        """Removes mutations successfully committed by peers."""
        if processed_ids:
            self.outbox.acknowledge(processed_ids)


class GossipMesh:
    """
    Simulates a multi-node peer-to-peer network mesh with dynamic partitions,
    airgapped isolation, and automated gossip synchronization.
    """

    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}
        self.partitions: Set[Tuple[str, str]] = set()

    def add_node(self, node: MeshNode) -> MeshNode:
        self.nodes[node.node_id] = node
        return node

    def create_node(self, node_id: str, name: Optional[str] = None) -> MeshNode:
        node = MeshNode(node_id, name)
        return self.add_node(node)

    def _pair_key(self, a: str, b: str) -> Tuple[str, str]:
        return (a, b) if a <= b else (b, a)

    def partition(self, node_a: str, node_b: str) -> None:
        """Cuts the communication link between two nodes."""
        self.partitions.add(self._pair_key(node_a, node_b))

    def isolate(self, node_id: str) -> None:
        """Isolates a node completely from all other nodes (e.g. flight/airgap mode)."""
        for other_id in self.nodes:
            if other_id != node_id:
                self.partition(node_id, other_id)

    def heal(self, node_a: str, node_b: str) -> None:
        """Restores the communication link between two nodes."""
        self.partitions.discard(self._pair_key(node_a, node_b))

    def heal_all(self) -> None:
        """Restores all network links to full connectivity."""
        self.partitions.clear()

    def is_connected(self, node_a: str, node_b: str) -> bool:
        """Checks whether two nodes have an active communication path."""
        if node_a == node_b:
            return True
        return self._pair_key(node_a, node_b) not in self.partitions

    def sync_round(self) -> Dict[str, Any]:
        """
        Executes one round of pairwise delta gossip exchange across all connected nodes.
        Returns metrics on deltas exchanged and convergence state.
        """
        node_ids = list(self.nodes.keys())
        total_deltas = 0
        exchanged_pairs = 0

        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                id_a, id_b = node_ids[i], node_ids[j]
                if self.is_connected(id_a, id_b):
                    node_a = self.nodes[id_a]
                    node_b = self.nodes[id_b]

                    # Node A -> Node B
                    delta_a = node_a.produce_sync_delta()
                    if delta_a["mutations"] or delta_a["counters"] or delta_a["sets"]:
                        ack_b = node_b.receive_sync_delta(delta_a)
                        node_a.acknowledge_remote(ack_b)
                        total_deltas += len(ack_b)

                    # Node B -> Node A
                    delta_b = node_b.produce_sync_delta()
                    if delta_b["mutations"] or delta_b["counters"] or delta_b["sets"]:
                        ack_a = node_a.receive_sync_delta(delta_b)
                        node_b.acknowledge_remote(ack_a)
                        total_deltas += len(ack_a)

                    exchanged_pairs += 1

        return {
            "exchanged_pairs": exchanged_pairs,
            "total_deltas": total_deltas,
            "connected": len(self.partitions) == 0,
        }

    def sync_until_stable(self, max_rounds: int = 10) -> int:
        """Repeatedly synchronizes until no pending outbox entries remain across connected nodes."""
        rounds = 0
        for _ in range(max_rounds):
            res = self.sync_round()
            rounds += 1
            # Check if all connected nodes have flushed outboxes
            total_pending = sum(len(n.outbox._queue) for n in self.nodes.values())
            if total_pending == 0:
                break
        return rounds

    def assert_converged(self, counter_names: Optional[List[str]] = None, set_names: Optional[List[str]] = None) -> bool:
        """
        Mathematically verifies Strong Eventual Consistency (SEC) across all nodes.
        Raises ContinuityIntegrityError if any divergence is found.
        """
        nodes_list = list(self.nodes.values())
        if len(nodes_list) < 2:
            return True

        # Check all counters
        all_counter_keys = set()
        for n in nodes_list:
            all_counter_keys.update(n.counters.keys())
        if counter_names:
            all_counter_keys = set(counter_names)

        for c_name in all_counter_keys:
            baseline = nodes_list[0].get_counter(c_name).value
            for n in nodes_list[1:]:
                val = n.get_counter(c_name).value
                if val != baseline:
                    raise ContinuityIntegrityError(
                        f"CRDT Divergence on Counter '{c_name}': {nodes_list[0].node_id}={baseline} vs {n.node_id}={val}"
                    )

        # Check all sets
        all_set_keys = set()
        for n in nodes_list:
            all_set_keys.update(n.sets.keys())
        if set_names:
            all_set_keys = set(set_names)

        for s_name in all_set_keys:
            baseline = nodes_list[0].get_set(s_name).elements
            for n in nodes_list[1:]:
                val = n.get_set(s_name).elements
                if val != baseline:
                    raise ContinuityIntegrityError(
                        f"CRDT Divergence on Set '{s_name}': {nodes_list[0].node_id}={baseline} vs {n.node_id}={val}"
                    )

        return True

    def topology_summary(self) -> Dict[str, Any]:
        """Returns structured metadata of the mesh state."""
        return {
            "total_nodes": len(self.nodes),
            "partitions": [list(p) for p in self.partitions],
            "nodes": {
                node_id: {
                    "name": n.name,
                    "clock": n.clock.to_dict(),
                    "outbox_pending": len(n.outbox._queue),
                    "ledger_blocks": len(n.ledger.entries),
                    "counters": {k: v.value for k, v in n.counters.items()},
                    "sets": {k: sorted(list(v.elements)) for k, v in n.sets.items()},
                }
                for node_id, n in self.nodes.items()
            }
        }

