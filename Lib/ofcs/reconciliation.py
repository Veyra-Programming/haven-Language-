"""
Open Financial Continuity Standard (OFCS) - Distributed Reconciliation Engine
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Enables offline branch banking to sync deterministically with central settlement hubs
without race conditions, balance drift, or double-spending.
"""

from typing import Any, Dict, List, Set, Tuple
from .ledger import OFCSFinancialLedger, DoubleEntryRecord


class ReconciliationReport:
    """Detailed summary of a completed reconciliation session."""
    def __init__(self, local_tx_count: int, remote_tx_count: int,
                 missing_in_remote: List[str], missing_in_local: List[str],
                 synced_successfully: bool):
        self.local_tx_count = local_tx_count
        self.remote_tx_count = remote_tx_count
        self.missing_in_remote = missing_in_remote
        self.missing_in_local = missing_in_local
        self.synced_successfully = synced_successfully

    def __repr__(self) -> str:
        return (f"ReconciliationReport(synced={self.synced_successfully}, "
                f"missing_in_remote={len(self.missing_in_remote)}, "
                f"missing_in_local={len(self.missing_in_local)})")


class ReconciliationEngine:
    """
    OFCS Offline-First Financial Reconciliation:
    Compares cryptographic state between two financial ledgers and settles differences.
    """
    def __init__(self, local_ledger: OFCSFinancialLedger):
        self.local_ledger = local_ledger

    def generate_state_digest(self) -> Dict[str, Any]:
        """Produces a lightweight cryptographic summary of settled transactions."""
        return {
            "ledger_name": self.local_ledger.ledger_name,
            "block_height": len(self.local_ledger.transactions),
            "head_hash": self.local_ledger.block_hashes[-1],
            "tx_ids": [tx.tx_id for tx in self.local_ledger.transactions]
        }

    def reconcile_with_remote(self, remote_ledger: OFCSFinancialLedger) -> ReconciliationReport:
        """
        Reconciles transactions between local and remote ledgers.
        Syncs any non-conflicting double-entry records.
        """
        local_tx_ids: Set[str] = set(self.local_ledger.settled_idempotency_keys.keys())
        remote_tx_ids: Set[str] = set(remote_ledger.settled_idempotency_keys.keys())

        missing_in_remote = list(local_tx_ids - remote_tx_ids)
        missing_in_local = list(remote_tx_ids - local_tx_ids)

        # Sync missing transactions from local into remote
        for tx in self.local_ledger.transactions:
            if tx.idempotency_key in missing_in_remote:
                # Ensure accounts exist in remote
                for acct_id, money in tx.debits + tx.credits:
                    if acct_id not in remote_ledger.accounts:
                        local_acct = self.local_ledger.accounts[acct_id]
                        remote_ledger.register_account(
                            type(local_acct)(acct_id, currency=local_acct.currency, allow_negative=local_acct.allow_negative)
                        )
                remote_ledger.post_transaction(tx)

        # Sync missing transactions from remote into local
        for tx in remote_ledger.transactions:
            if tx.idempotency_key in missing_in_local:
                # Ensure accounts exist in local
                for acct_id, money in tx.debits + tx.credits:
                    if acct_id not in self.local_ledger.accounts:
                        remote_acct = remote_ledger.accounts[acct_id]
                        self.local_ledger.register_account(
                            type(remote_acct)(acct_id, currency=remote_acct.currency, allow_negative=remote_acct.allow_negative)
                        )
                self.local_ledger.post_transaction(tx)

        synced = (len(self.local_ledger.transactions) == len(remote_ledger.transactions))
        return ReconciliationReport(
            local_tx_count=len(self.local_ledger.transactions),
            remote_tx_count=len(remote_ledger.transactions),
            missing_in_remote=missing_in_remote,
            missing_in_local=missing_in_local,
            synced_successfully=synced
        )

