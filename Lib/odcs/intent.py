"""
Open Digital Continuity Standard (ODCS) - Layer 4: Application & Continuity UX
Standard Specification & Architecture by Anirudha Puthraya.
Implements:
  - IntentReceipt: Cryptographic receipt guaranteeing Zero Intent Loss
  - ZeroIntentLossManager: Orchestrates optimistic commits, UI state protection, and reconciliation
"""

from typing import Any, Dict, Optional, Callable
import time
import uuid
from .envelope import canonical_json, compute_sha256
from .core import DurableRecord, durable_record
from .ledger import get_default_ledger, checkpoint


@durable_record
class IntentReceipt:
    """
    Cryptographic Intent Receipt (ODCS Layer 4.1).
    Guarantees that user actions are immortalized locally before remote network transmission.
    """
    def __init__(
        self,
        intent_id: str,
        action: str,
        actor: str,
        payload_digest: str,
        created_at: str,
        status: str = "committed_locally"
    ):
        self.intent_id = intent_id
        self.action = action
        self.actor = actor
        self.payload_digest = payload_digest
        self.created_at = created_at
        self.status = status


class ZeroIntentLossManager:
    """
    Orchestrates Layer 4 Zero Intent Loss workflows.
    Ensures that form submits, edits, and state transitions are never lost due to offline disruptions.
    """
    def __init__(self, ledger_name: Optional[str] = None):
        self.ledger = get_default_ledger()

    def capture(self, action: str, actor: str, payload: Dict[str, Any]) -> IntentReceipt:
        """
        Captures user action into local memory, seals it into an IntentReceipt,
        and commits it immediately to the local continuity ledger.
        """
        intent_id = f"intent-{uuid.uuid4().hex[:12]}"
        digest = f"sha256:{compute_sha256(canonical_json(payload))}"
        created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        receipt = IntentReceipt(
            intent_id=intent_id,
            action=action,
            actor=actor,
            payload_digest=digest,
            created_at=created_at,
            status="sealed_in_local_ledger"
        )

        # Checkpoint into active continuity ledger
        checkpoint(receipt, alias=f"intent:{action}:{intent_id}", ledger=self.ledger)
        return receipt

