"""
Open Financial Continuity Standard (OFCS) SDK for Haven Programming Language
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Core Architecture:
  1. Exact Decimal Representation & Monetary Arithmetic (Money, Currency, ExchangeRate)
  2. Double-Entry Cryptographic Ledger (DoubleEntryRecord, FinancialAccount, OFCSFinancialLedger)
  3. Financial Transaction Annotations (@FinancialTransaction, @Idempotent, @ZeroDrift)
  4. Distributed Offline Reconciliation (ReconciliationEngine, ReconciliationReport)
"""

from .money import (
    Money,
    Currency,
    CurrencyMismatchError,
    ExchangeRate,
    get_currency,
    USD, EUR, GBP, INR, JPY, BTC, HVN
)
from .ledger import (
    DoubleEntryRecord,
    FinancialAccount,
    OFCSFinancialLedger,
    UnbalancedTransactionError,
    InsufficientFundsError,
    DuplicateTransactionError,
    _GLOBAL_FINANCIAL_LEDGER
)
from .annotations import (
    FinancialTransaction,
    Idempotent,
    ZeroDrift,
    ZeroDriftViolationError
)
from .reconciliation import (
    ReconciliationEngine,
    ReconciliationReport
)

__version__ = "1.0.0"
__author__ = "Anirudha Puthraya"
__standard__ = "Open Financial Continuity Standard (OFCS)"
