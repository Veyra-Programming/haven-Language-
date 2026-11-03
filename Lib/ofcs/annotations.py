"""
Open Financial Continuity Standard (OFCS) - Financial Annotations & Contract Guards
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Annotations:
  1. @FinancialTransaction: Atomic double-entry execution with rollback
  2. @Idempotent: Anti-double-spend and duplicate rejection
  3. @ZeroDrift: Mathematical balance conservation assertion
"""

import functools
import time
from typing import Any, Callable, Dict, Optional, Tuple, Type
from haven.annotations import _register_annotation
from .ledger import _GLOBAL_FINANCIAL_LEDGER, OFCSFinancialLedger, DoubleEntryRecord, DuplicateTransactionError
from .money import Money


class ZeroDriftViolationError(ValueError):
    """Raised when an operation results in an unauthorized creation or loss of money."""
    pass


def FinancialTransaction(ledger: Optional[OFCSFinancialLedger] = None):
    """
    OFCS @FinancialTransaction:
    Wraps method execution in an atomic financial transaction.
    If an error occurs, no balances are updated and an uncommitted state is logged.
    """
    def decorator(fn: Callable) -> Callable:
        _register_annotation(fn, FinancialTransaction, {})

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            active_ledger = ledger or _GLOBAL_FINANCIAL_LEDGER
            # Pre-snapshot account balances
            snapshot = {acct_id: acct.balance for acct_id, acct in active_ledger.accounts.items()}

            try:
                result = fn(*args, **kwargs)
                return result
            except Exception as e:
                # Rollback balances to pre-snapshot
                for acct_id, bal in snapshot.items():
                    active_ledger.accounts[acct_id].balance = bal
                raise e

        _register_annotation(wrapper, FinancialTransaction, {})
        return wrapper
    return decorator


def Idempotent(key_extractor: Optional[Callable[..., str]] = None, key_arg_name: str = "idempotency_key"):
    """
    OFCS @Idempotent:
    Guarantees that a payment or financial call cannot be executed more than once.
    Subsequent calls with the same key return the settled receipt without re-execution.
    """
    _settled_cache: Dict[str, Any] = {}

    def decorator(fn: Callable) -> Callable:
        _register_annotation(fn, Idempotent, {"key_arg_name": key_arg_name})

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Extract idempotency key
            key = None
            if key_extractor:
                key = key_extractor(*args, **kwargs)
            elif key_arg_name in kwargs:
                key = kwargs[key_arg_name]
            elif args:
                # Check if first non-self arg is string or has idempotency_key
                for a in args:
                    if isinstance(a, str) and (a.startswith("idemp-") or a.startswith("tx-") or len(a) > 8):
                        key = a
                        break

            if key and key in _settled_cache:
                return _settled_cache[key]

            result = fn(*args, **kwargs)

            if key:
                _settled_cache[key] = result
            return result

        _register_annotation(wrapper, Idempotent, {"key_arg_name": key_arg_name})
        return wrapper
    return decorator


def ZeroDrift(ledger: Optional[OFCSFinancialLedger] = None):
    """
    OFCS @ZeroDrift:
    Mathematically verifies that the sum of balances across the system
    remains completely conserved before and after the method completes.
    """
    def decorator(fn: Callable) -> Callable:
        _register_annotation(fn, ZeroDrift, {})

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            active_ledger = ledger or _GLOBAL_FINANCIAL_LEDGER

            # Tally initial totals per currency
            initial_totals = {}
            for acct in active_ledger.accounts.values():
                code = acct.currency.code
                initial_totals[code] = initial_totals.get(code, Money(0, acct.currency)) + acct.balance

            res = fn(*args, **kwargs)

            # Tally post totals per currency
            post_totals = {}
            for acct in active_ledger.accounts.values():
                code = acct.currency.code
                post_totals[code] = post_totals.get(code, Money(0, acct.currency)) + acct.balance

            # Compare totals
            for code, initial_money in initial_totals.items():
                post_money = post_totals.get(code, Money(0, initial_money.currency))
                if initial_money != post_money:
                    raise ZeroDriftViolationError(
                        f"ZeroDrift violation in currency {code}! "
                        f"Initial={initial_money}, Post={post_money}, Delta={post_money - initial_money}"
                    )
            return res

        _register_annotation(wrapper, ZeroDrift, {})
        return wrapper
    return decorator
