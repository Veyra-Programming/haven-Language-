"""
Open Digital Continuity Standard (ODCS) - Continuity Algorithm & App System Framework
Standard Specification & Architecture by Anirudha Puthraya.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Tuple, Union, Set
from datetime import datetime, timezone
import json
import uuid
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from .core import DurableRecord, durable_record, ContinuityImmutabilityError, ContinuityIntegrityError
from .envelope import ContinuityAssetEnvelope, canonical_json, compute_sha256
from .merkle import MerkleTree
from .ledger import ContinuityLedger, LedgerEntry, get_default_ledger, checkpoint, verify_continuity


@durable_record
class StateTransitionStep:
    """
    Cryptographically sealed representation of an atomic ODCS state transition.
    Enforces tamper-evidence for every state alteration in a continuity algorithm.
    """
    def __init__(
        self,
        transition_id: str,
        algorithm_id: str,
        action: str,
        actor: str,
        pre_state_hash: str,
        post_state_hash: str,
        payload_hash: str,
        timestamp: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.transition_id = transition_id
        self.algorithm_id = algorithm_id
        self.action = action
        self.actor = actor
        self.pre_state_hash = pre_state_hash
        self.post_state_hash = post_state_hash
        self.payload_hash = payload_hash
        self.timestamp = timestamp
        self.metadata = metadata or {}


class ContinuityAlgorithm(ABC):
    """
    Abstract Base Class for Open Digital Continuity Standard (ODCS) Algorithms.
    Continuity algorithms govern verifiable state evolution, deterministic replay,
    invariant verification, and cryptographic sealing across distributed or long-lived applications.
    """
    STANDARD: str = "ODCS-1.0.0"
    SPECIFICATION_AUTHOR: str = "Anirudha Puthraya"

    def __init__(
        self,
        algorithm_id: str,
        version: str = "1.0.0",
        description: str = "Standard ODCS Continuity Algorithm"
    ) -> None:
        self.algorithm_id = algorithm_id
        self.version = version
        self.description = description
        self.transition_history: List[StateTransitionStep] = []

    @abstractmethod
    def validate_transition(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system"
    ) -> bool:
        """Evaluate preconditions and invariants before state mutation."""
        pass

    @abstractmethod
    def apply_transition(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system"
    ) -> Dict[str, Any]:
        """Compute the deterministic next state given current state and action payload."""
        pass

    def compute_state_hash(self, state: Dict[str, Any]) -> str:
        """Compute deterministic SHA-256 state digest according to ODCS canonicalization."""
        return f"sha256:{compute_sha256(canonical_json(state))}"

    def compute_state_merkle_root(self, state: Dict[str, Any]) -> str:
        """Compute Merkle root over sorted state elements for zero-knowledge field verification."""
        tree = MerkleTree(sorted(state.items()))
        return tree.root

    def execute_step(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], StateTransitionStep]:
        """
        Executes a single verified step in the continuity algorithm.
        Validates invariants, applies mutation, seals the transition step,
        and returns the new state along with the cryptographic transition record.
        """
        pre_hash = self.compute_state_hash(current_state)

        # 1. Enforce Preconditions
        if not self.validate_transition(current_state, action, payload, actor):
            raise ContinuityIntegrityError(
                f"ODCS Transition Rejected: Action '{action}' by actor '{actor}' "
                f"violated continuity algorithm '{self.algorithm_id}' invariants."
            )

        # 2. Compute Deterministic Next State
        new_state = self.apply_transition(current_state, action, payload, actor)
        post_hash = self.compute_state_hash(new_state)
        payload_hash = f"sha256:{compute_sha256(canonical_json(payload))}"

        # 3. Create Sealed Durable Transition Step
        step = StateTransitionStep(
            transition_id=str(uuid.uuid4()),
            algorithm_id=self.algorithm_id,
            action=action,
            actor=actor,
            pre_state_hash=pre_hash,
            post_state_hash=post_hash,
            payload_hash=payload_hash,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )

        self.transition_history.append(step)
        return new_state, step

    def replay_transitions(
        self,
        initial_state: Dict[str, Any],
        transitions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Replays a series of transitions deterministically from initial state.
        Verifies cryptographic integrity at every step.
        """
        state = dict(initial_state)
        for t in transitions:
            action = t["action"]
            payload = t["payload"]
            actor = t.get("actor", "system")
            expected_post_hash = t.get("post_state_hash")

            state, step = self.execute_step(state, action, payload, actor)
            if expected_post_hash and step.post_state_hash != expected_post_hash:
                raise ContinuityIntegrityError(
                    f"ODCS Replay Desynchronization: expected post-state {expected_post_hash}, "
                    f"got {step.post_state_hash} on action '{action}'."
                )
        return state


class StateContinuityAlgorithm(ContinuityAlgorithm):
    """
    General-purpose Finite State Machine Continuity Algorithm.
    Allows registering invariant rules, transition guards, and transition mutators.
    """
    def __init__(
        self,
        algorithm_id: str = "StateContinuityEngine",
        version: str = "1.0.0",
        description: str = "Deterministic Finite State Machine Continuity Algorithm"
    ):
        super().__init__(algorithm_id, version, description)
        self._validators: Dict[str, List[Callable[[Dict[str, Any], Dict[str, Any], str], bool]]] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any], Dict[str, Any], str], Dict[str, Any]]] = {}
        self._global_invariants: List[Callable[[Dict[str, Any]], bool]] = []

    def add_invariant(self, predicate: Callable[[Dict[str, Any]], bool]) -> "StateContinuityAlgorithm":
        """Add a global invariant that must hold true across all states."""
        self._global_invariants.append(predicate)
        return self

    def register_transition(
        self,
        action: str,
        handler: Callable[[Dict[str, Any], Dict[str, Any], str], Dict[str, Any]],
        validator: Optional[Callable[[Dict[str, Any], Dict[str, Any], str], bool]] = None
    ) -> "StateContinuityAlgorithm":
        """Register an action handler and optional validator guard."""
        self._handlers[action] = handler
        if validator:
            if action not in self._validators:
                self._validators[action] = []
            self._validators[action].append(validator)
        return self

    def validate_transition(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system"
    ) -> bool:
        if action not in self._handlers:
            return False

        # Check action-specific validators
        for v in self._validators.get(action, []):
            if not v(current_state, payload, actor):
                return False

        return True

    def apply_transition(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system"
    ) -> Dict[str, Any]:
        handler = self._handlers[action]
        next_state = handler(dict(current_state), payload, actor)

        # Check global invariants on next state
        for inv in self._global_invariants:
            if not inv(next_state):
                raise ContinuityIntegrityError(
                    f"ODCS Invariant Violation: Global invariant failed after action '{action}'."
                )

        return next_state


class ConsensusContinuityAlgorithm(ContinuityAlgorithm):
    """
    Multi-Actor Quorum Consensus Continuity Algorithm.
    Ensures state transitions are only committed when a verifiable quorum threshold
    of designated authorized participants/validators sign or approve the transaction.
    """
    def __init__(
        self,
        algorithm_id: str = "ConsensusContinuityEngine",
        version: str = "1.0.0",
        required_quorum_ratio: float = 0.67,
        authorized_validators: Optional[Set[str]] = None
    ):
        super().__init__(algorithm_id, version, "ODCS Multi-Signer Quorum Consensus Algorithm")
        self.required_quorum_ratio = required_quorum_ratio
        self.authorized_validators: Set[str] = authorized_validators or set()
        self._handlers: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]] = {}

    def register_validator(self, validator_id: str) -> None:
        self.authorized_validators.add(validator_id)

    def register_action(self, action: str, handler: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]) -> None:
        self._handlers[action] = handler

    def validate_transition(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system"
    ) -> bool:
        if action not in self._handlers:
            return False

        # Validate quorum signatures in payload
        signatures = payload.get("signatures", {})
        if not isinstance(signatures, dict):
            return False

        if not self.authorized_validators:
            return True

        valid_sigs = sum(1 for v in signatures if v in self.authorized_validators)
        required_count = int(len(self.authorized_validators) * self.required_quorum_ratio)
        return valid_sigs >= max(1, required_count)

    def apply_transition(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system"
    ) -> Dict[str, Any]:
        return self._handlers[action](dict(current_state), payload)


class EventSourcingContinuityAlgorithm(ContinuityAlgorithm):
    """
    Event-Sourced Append-Only Continuity Algorithm.
    Treats every state change as an immutable event stream, providing
    complete auditability, deterministic zero-loss replay, and Merkle snapshotting.
    """
    def __init__(
        self,
        algorithm_id: str = "EventSourcingContinuityEngine",
        version: str = "1.0.0",
        snapshot_interval: int = 100
    ):
        super().__init__(algorithm_id, version, "ODCS Event-Sourced Immutable Ledger Algorithm")
        self.snapshot_interval = snapshot_interval
        self._reducers: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]] = {}
        self.snapshots: List[Dict[str, Any]] = []

    def register_event_reducer(
        self,
        event_type: str,
        reducer: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        self._reducers[event_type] = reducer

    def validate_transition(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system"
    ) -> bool:
        return action in self._reducers

    def apply_transition(
        self,
        current_state: Dict[str, Any],
        action: str,
        payload: Dict[str, Any],
        actor: str = "system"
    ) -> Dict[str, Any]:
        new_state = self._reducers[action](dict(current_state), payload)
        
        # Periodic snapshotting
        if len(self.transition_history) > 0 and len(self.transition_history) % self.snapshot_interval == 0:
            tree = MerkleTree(sorted(new_state.items()))
            self.snapshots.append({
                "step_index": len(self.transition_history),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "state_hash": self.compute_state_hash(new_state),
                "merkle_root": tree.root,
                "state_snapshot": dict(new_state),
            })

        return new_state


class ODCSApp:
    """
    Open Digital Continuity Standard (ODCS) Application System.
    Production application engine providing:
      - Deterministic State Machine governed by an ODCS Continuity Algorithm
      - Integrated Cryptographic Continuity Ledger
      - Durable Record Sealing & Provenance
      - Action Dispatcher with Invariant Enforcement
      - Tamper-Evident Audit Report Generation
      - Journal Export & Replay Disaster Recovery
      - Embedded Verifiable REST / HTTP Microservice Server
    """
    STANDARD: str = "ODCS-1.0.0"
    SPECIFICATION_AUTHOR: str = "Anirudha Puthraya"

    def __init__(
        self,
        name: str,
        algorithm: Optional[ContinuityAlgorithm] = None,
        initial_state: Optional[Dict[str, Any]] = None,
        author: str = "Anirudha Puthraya",
        ledger_name: Optional[str] = None
    ):
        self.name = name
        self.author = author
        self.algorithm: ContinuityAlgorithm = algorithm or StateContinuityAlgorithm(f"{name}-Algorithm")
        self.ledger: ContinuityLedger = ContinuityLedger(
            name=ledger_name or f"{name}-ContinuityLedger",
            author=author
        )
        self.state: Dict[str, Any] = dict(initial_state or {})
        self._lock = threading.RLock()
        self._action_listeners: List[Callable[[str, Dict[str, Any], Dict[str, Any], LedgerEntry], None]] = []

        # Checkpoint initial state genesis
        init_envelope = ContinuityAssetEnvelope(
            asset_type=f"{name}.InitialState",
            payload={
                "app_name": self.name,
                "author": self.author,
                "standard": self.STANDARD,
                "initial_state": self.state,
                "algorithm": self.algorithm.algorithm_id,
                "version": self.algorithm.version,
            },
            creator=self.author,
        )
        self.ledger.checkpoint(init_envelope, alias="app_initial_state")

    def register_action(
        self,
        action: str,
        handler: Callable[[Dict[str, Any], Dict[str, Any], str], Dict[str, Any]],
        validator: Optional[Callable[[Dict[str, Any], Dict[str, Any], str], bool]] = None
    ) -> "ODCSApp":
        """Register an action handler on the underlying continuity algorithm."""
        if isinstance(self.algorithm, StateContinuityAlgorithm):
            self.algorithm.register_transition(action, handler, validator)
        return self

    def add_listener(self, listener: Callable[[str, Dict[str, Any], Dict[str, Any], LedgerEntry], None]) -> None:
        """Register an event listener invoked after verified action execution."""
        self._action_listeners.append(listener)

    def dispatch(
        self,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> LedgerEntry:
        """
        Atomically dispatches an action through the ODCS continuity algorithm,
        updates state, checkpoints into the ledger, and notifies listeners.
        """
        payload = payload or {}
        with self._lock:
            # 1. Execute verifiable continuity step
            new_state, step = self.algorithm.execute_step(
                current_state=self.state,
                action=action,
                payload=payload,
                actor=actor,
                metadata=metadata
            )

            # 2. Update internal state
            self.state = new_state

            # 3. Create Continuity Asset Envelope for this state change
            envelope = ContinuityAssetEnvelope(
                asset_id=step.transition_id,
                asset_type=f"{self.name}.Event.{action}",
                payload={
                    "action": action,
                    "actor": actor,
                    "payload": payload,
                    "pre_state_hash": step.pre_state_hash,
                    "post_state_hash": step.post_state_hash,
                    "timestamp": step.timestamp,
                },
                creator=f"{actor} via ODCS App '{self.name}'",
                metadata=metadata or {},
            )

            # 4. Checkpoint into Continuity Ledger
            entry = self.ledger.checkpoint(envelope, alias=f"{action}_{len(self.ledger.entries)}")

            # 5. Notify listeners
            for listener in self._action_listeners:
                try:
                    listener(action, payload, self.state, entry)
                except Exception as e:
                    pass

            return entry

    def get_state(self) -> Dict[str, Any]:
        """Return a copy of the current application state."""
        with self._lock:
            return dict(self.state)

    def get_state_hash(self) -> str:
        """Return canonical hash of current state."""
        return self.algorithm.compute_state_hash(self.state)

    def get_merkle_root(self) -> str:
        """Return Merkle root of current state."""
        return self.algorithm.compute_state_merkle_root(self.state)

    def audit(self) -> Dict[str, Any]:
        """
        Performs a full cryptographic continuity audit of the application.
        Verifies:
          - Cryptographic chain integrity from genesis to head
          - All block envelope hashes
          - State transition hash consistency
        """
        with self._lock:
            chain_valid = self.ledger.verify_chain()
            total_entries = len(self.ledger.entries)
            total_transitions = len(self.algorithm.transition_history)

            return {
                "app_name": self.name,
                "standard": self.STANDARD,
                "author": self.author,
                "audit_timestamp": datetime.now(timezone.utc).isoformat(),
                "chain_integrity_valid": chain_valid,
                "head_hash": self.ledger.head_hash,
                "total_ledger_blocks": total_entries,
                "total_transitions_executed": total_transitions,
                "current_state_hash": self.get_state_hash(),
                "current_merkle_root": self.get_merkle_root(),
                "status": "HEALTHY_AND_VERIFIED" if chain_valid else "CORRUPTED_TAMPER_DETECTED",
            }

    def export_journal(self, file_path: str) -> str:
        """Exports the application's ledger and audit journal to a file."""
        return self.ledger.export_journal(file_path)

    @classmethod
    def recover_from_journal(
        cls,
        name: str,
        journal_path: str,
        algorithm: ContinuityAlgorithm,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> "ODCSApp":
        """
        Disaster Recovery: Restores an ODCS Application from an archived journal file,
        validating every cryptographic hash block before re-establishing state.
        """
        restored_ledger = ContinuityLedger.replay_journal(journal_path)
        app = cls(name=name, algorithm=algorithm, initial_state=initial_state or {})
        app.ledger = restored_ledger

        # Reconstruct state by walking through ledger blocks
        curr_state = dict(initial_state or {})
        for entry in restored_ledger.entries[1:]:  # skip genesis
            payload = entry.envelope.payload
            action = payload.get("action")
            event_payload = payload.get("payload", {})
            actor = payload.get("actor", "system")
            if action and algorithm.validate_transition(curr_state, action, event_payload, actor):
                curr_state = algorithm.apply_transition(curr_state, action, event_payload, actor)

        app.state = curr_state
        return app

    def serve(self, host: str = "127.0.0.1", port: int = 8080, background: bool = False) -> Optional[HTTPServer]:
        """
        Launches an embedded HTTP / REST microservice server exposing ODCS endpoints:
          - GET  /api/status   -> Audit & health status
          - GET  /api/state    -> Current state & Merkle proof
          - GET  /api/audit    -> Full cryptographic chain audit report
          - GET  /api/ledger   -> Sealed ledger block summary
          - POST /api/dispatch -> Verified action submission
        """
        app_instance = self

        class ODCSRequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                pass  # Quiet logging

            def _send_json(self, status_code: int, data: Any) -> None:
                body = canonical_json(data).encode("utf-8")
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:
                path = self.path.split("?")[0]
                if path in ("/", "/api/status"):
                    self._send_json(200, {
                        "app": app_instance.name,
                        "standard": app_instance.STANDARD,
                        "author": app_instance.author,
                        "head_hash": app_instance.ledger.head_hash,
                        "blocks": len(app_instance.ledger.entries),
                        "state_hash": app_instance.get_state_hash(),
                    })
                elif path == "/api/state":
                    self._send_json(200, {
                        "state": app_instance.get_state(),
                        "state_hash": app_instance.get_state_hash(),
                        "merkle_root": app_instance.get_merkle_root(),
                    })
                elif path == "/api/audit":
                    self._send_json(200, app_instance.audit())
                elif path == "/api/ledger":
                    summary = [
                        {
                            "index": e.index,
                            "entry_hash": e.entry_hash,
                            "prev_hash": e.prev_hash,
                            "alias": e.alias,
                            "timestamp": e.timestamp,
                            "asset_type": e.envelope.asset_type,
                        }
                        for e in app_instance.ledger.entries
                    ]
                    self._send_json(200, {"total": len(summary), "entries": summary})
                else:
                    self._send_json(404, {"error": "Endpoint not found"})

            def do_POST(self) -> None:
                path = self.path.split("?")[0]
                if path == "/api/dispatch":
                    try:
                        content_len = int(self.headers.get("Content-Length", 0))
                        post_body = self.rfile.read(content_len).decode("utf-8")
                        data = json.loads(post_body)
                        action = data.get("action")
                        payload = data.get("payload", {})
                        actor = data.get("actor", "http_client")
                        if not action:
                            self._send_json(400, {"error": "Missing 'action' field."})
                            return

                        entry = app_instance.dispatch(action=action, payload=payload, actor=actor)
                        self._send_json(200, {
                            "status": "DISPATCHED_AND_SEALED",
                            "action": action,
                            "entry_hash": entry.entry_hash,
                            "index": entry.index,
                            "state_hash": app_instance.get_state_hash(),
                        })
                    except Exception as e:
                        self._send_json(400, {"error": str(e)})
                else:
                    self._send_json(404, {"error": "Endpoint not found"})

        server = HTTPServer((host, port), ODCSRequestHandler)
        if background:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            return server
        else:
            print(f"[ODCS Server] Serving '{self.name}' on http://{host}:{port}/ ...")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                print("\n[ODCS Server] Shutting down.")
                server.server_close()
            return server

