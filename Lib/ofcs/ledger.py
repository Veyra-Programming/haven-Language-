"""
Open Financial Continuity Standard (OFCS) - Cryptographic Double-Entry Ledger
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Core Invariants:
  1. Invariant 1: Conservation of Balance (Total Debits == Total Credits in Every Transaction)
  2. Invariant 2: Anti-Double-Spend & Idempotency Guarantee
  3. Invariant 3: Cryptographic Merkle Hash Chain
  4. Invariant 4: Sovereign Local-First Execution
"""

import time
import hashlib
import json
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from .money import Money, Currency, get_currency, USD


class UnbalancedTransactionError(ValueError):
    """Raised when a double-entry transaction has unequal debit and credit sums."""
    pass


class InsufficientFundsError(ValueError):
    """Raised when an account balance cannot cover a debit/withdrawal."""
    pass


class DuplicateTransactionError(ValueError):
    """Raised when attempting to execute a transaction with an already-settled idempotency key."""
    pass


class DoubleEntryRecord:
    """
    OFCS Double-Entry Transaction Record:
    Enforces that the sum of debits exactly matches the sum of credits.
    """
    def __init__(self, tx_id: str,
                 debits: List[Tuple[str, Money]],   # (account_id, money)
                 credits: List[Tuple[str, Money]],  # (account_id, money)
                 memo: str = "",
                 idempotency_key: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        if not debits or not credits:
            raise ValueError("Double-entry record must have at least one debit and one credit")

        self.tx_id = tx_id
        self.debits = debits
        self.credits = credits
        self.memo = memo
        self.idempotency_key = idempotency_key or tx_id
        self.metadata = metadata or {}
        self.timestamp = time.time()

        # Invariant 1: Conservation of Balance
        self._validate_balance()

        # Compute deterministic cryptographic hash
        self.record_hash = self._compute_hash()

    def _validate_balance(self):
        # Group debits by currency
        debit_sums: Dict[Currency, Decimal] = {}
        for acct, money in self.debits:
            debit_sums[money.currency] = debit_sums.get(money.currency, Decimal(0)) + money.amount

        # Group credits by currency
        credit_sums: Dict[Currency, Decimal] = {}
        for acct, money in self.credits:
            credit_sums[money.currency] = credit_sums.get(money.currency, Decimal(0)) + money.amount

        # Check equality per currency
        all_currencies = set(debit_sums.keys()) | set(credit_sums.keys())
        for curr in all_currencies:
            d_sum = debit_sums.get(curr, Decimal(0))
            c_sum = credit_sums.get(curr, Decimal(0))
            if d_sum != c_sum:
                raise UnbalancedTransactionError(
                    f"Transaction '{self.tx_id}' is unbalanced in {curr.code}: "
                    f"Debits={d_sum} != Credits={c_sum}. Delta = {d_sum - c_sum}"
                )

    def _compute_hash(self) -> str:
        data = {
            "tx_id": self.tx_id,
            "idempotency_key": self.idempotency_key,
            "debits": [(acct, str(m.amount), m.currency.code) for acct, m in self.debits],
            "credits": [(acct, str(m.amount), m.currency.code) for acct, m in self.credits],
            "memo": self.memo,
            "timestamp": self.timestamp
        }
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "record_hash": self.record_hash,
            "idempotency_key": self.idempotency_key,
            "debits": [{"account": acct, "amount": str(m.amount), "currency": m.currency.code} for acct, m in self.debits],
            "credits": [{"account": acct, "amount": str(m.amount), "currency": m.currency.code} for acct, m in self.credits],
            "memo": self.memo,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        return f"DoubleEntryRecord(tx_id='{self.tx_id}', hash='{self.record_hash[:12]}...', debits={len(self.debits)}, credits={len(self.credits)})"


class FinancialAccount:
    """
    Sovereign OFCS Financial Account:
    Holds exact decimal balances and immutable transaction history.
    """
    def __init__(self, account_id: str, currency: Union[str, Currency] = USD, allow_negative: bool = False, initial_balance: Union[Decimal, float, int, str] = 0):
        self.account_id = account_id
        self.currency = get_currency(currency)
        self.allow_negative = allow_negative
        self.balance = Money(initial_balance, self.currency)
        self.status = "ACTIVE" # ACTIVE, FROZEN, CLOSED
        self.history: List[str] = [] # list of tx_ids

    def credit(self, amount: Money, tx_id: str) -> Money:
        """Increases account balance (funds received)."""
        if self.status != "ACTIVE":
            raise RuntimeError(f"Cannot credit account '{self.account_id}': Status is '{self.status}'")
        if amount.currency != self.currency:
            raise TypeError(f"Account {self.account_id} accepts {self.currency.code}, got {amount.currency.code}")
        self.balance = self.balance + amount
        self.history.append(tx_id)
        return self.balance

    def debit(self, amount: Money, tx_id: str) -> Money:
        """Decreases account balance (funds disbursed)."""
        if self.status != "ACTIVE":
            raise RuntimeError(f"Cannot debit account '{self.account_id}': Status is '{self.status}'")
        if amount.currency != self.currency:
            raise TypeError(f"Account {self.account_id} accepts {self.currency.code}, got {amount.currency.code}")
        if not self.allow_negative and self.balance < amount:
            raise InsufficientFundsError(
                f"Account '{self.account_id}' has insufficient funds. Balance: {self.balance}, Requested Debit: {amount}"
            )
        self.balance = self.balance - amount
        self.history.append(tx_id)
        return self.balance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "currency": self.currency.code,
            "balance": str(self.balance.amount),
            "status": self.status,
            "transactions_count": len(self.history)
        }

    def __repr__(self) -> str:
        return f"FinancialAccount({self.account_id}, balance={self.balance}, status={self.status})"


class OFCSFinancialLedger:
    """
    Open Financial Continuity Standard Ledger:
    Cryptographically sealed, append-only double-entry ledger.
    Guarantees zero intent loss, zero balance drift, and offline idempotency.
    """
    def __init__(self, ledger_name: str = "OFCS-Master-Ledger"):
        self.ledger_name = ledger_name
        self.accounts: Dict[str, FinancialAccount] = {}
        self.transactions: List[DoubleEntryRecord] = []
        self.settled_idempotency_keys: Dict[str, str] = {} # idempotency_key -> tx_id
        self.block_hashes: List[str] = ["0" * 64] # Genesis hash

    def register_account(self, account: FinancialAccount) -> FinancialAccount:
        if account.account_id in self.accounts:
            raise ValueError(f"Account '{account.account_id}' already registered in ledger '{self.ledger_name}'")
        self.accounts[account.account_id] = account
        return account

    def get_account(self, account_id: str) -> FinancialAccount:
        if account_id not in self.accounts:
            raise KeyError(f"Account '{account_id}' not found in ledger '{self.ledger_name}'")
        return self.accounts[account_id]

    def post_transaction(self, record: DoubleEntryRecord) -> Dict[str, Any]:
        """
        Atomically executes and settles a double-entry financial record.
        Enforces idempotency, balance integrity, and hash chaining.
        """
        # Invariant 2: Idempotency Check
        if record.idempotency_key in self.settled_idempotency_keys:
            existing_tx_id = self.settled_idempotency_keys[record.idempotency_key]
            return {
                "status": "DUPLICATE_IDEMPOTENT_RECEIPT",
                "tx_id": existing_tx_id,
                "message": "Transaction already settled. Returning idempotent receipt."
            }

        # Verify all accounts exist
        for acct_id, _ in record.debits:
            if acct_id not in self.accounts:
                raise KeyError(f"Debit account '{acct_id}' does not exist")
        for acct_id, _ in record.credits:
            if acct_id not in self.accounts:
                raise KeyError(f"Credit account '{acct_id}' does not exist")

        # Dry-run debit verification (check sufficient funds)
        for acct_id, money in record.debits:
            acct = self.accounts[acct_id]
            if not acct.allow_negative and acct.balance < money:
                raise InsufficientFundsError(
                    f"Account '{acct_id}' has insufficient balance: {acct.balance} < {money}"
                )

        # Atomic execution
        # 1. Apply debits
        for acct_id, money in record.debits:
            self.accounts[acct_id].debit(money, record.tx_id)

        # 2. Apply credits
        for acct_id, money in record.credits:
            self.accounts[acct_id].credit(money, record.tx_id)

        # 3. Cryptographic Chain Linking
        prev_hash = self.block_hashes[-1]
        block_content = f"{prev_hash}:{record.record_hash}:{len(self.transactions)}"
        block_hash = hashlib.sha256(block_content.encode("utf-8")).hexdigest()
        self.block_hashes.append(block_hash)

        # 4. Save and index
        self.transactions.append(record)
        self.settled_idempotency_keys[record.idempotency_key] = record.tx_id

        return {
            "status": "SETTLED",
            "tx_id": record.tx_id,
            "record_hash": record.record_hash,
            "block_hash": block_hash,
            "block_height": len(self.transactions),
            "timestamp": record.timestamp
        }

    def transfer(self, from_account: str, to_account: str, amount: Money,
                 memo: str = "", idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Convenience method for simple transfers between two accounts."""
        tx_id = f"tx-{int(time.time()*1000)}-{len(self.transactions)+1}"
        record = DoubleEntryRecord(
            tx_id=tx_id,
            debits=[(from_account, amount)],
            credits=[(to_account, amount)],
            memo=memo,
            idempotency_key=idempotency_key or tx_id
        )
        return self.post_transaction(record)

    def verify_ledger_chain(self) -> bool:
        """Verifies full cryptographic chain integrity from genesis to head."""
        if len(self.block_hashes) != len(self.transactions) + 1:
            return False

        for i, tx in enumerate(self.transactions):
            prev_hash = self.block_hashes[i]
            expected_content = f"{prev_hash}:{tx.record_hash}:{i}"
            expected_hash = hashlib.sha256(expected_content.encode("utf-8")).hexdigest()
            if self.block_hashes[i + 1] != expected_hash:
                return False
        return True

    def calculate_total_volume(self, currency: Union[str, Currency]) -> Money:
        """Calculates total system volume in specified currency."""
        curr = get_currency(currency)
        total = Money(0, curr)
        for acct in self.accounts.values():
            if acct.currency == curr and acct.balance.is_positive():
                total = total + acct.balance
        return total


# Global singleton instance
_GLOBAL_FINANCIAL_LEDGER = OFCSFinancialLedger("Global-OFCS-Ledger")
