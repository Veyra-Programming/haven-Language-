"""
Haven Backend Framework - OFCS Financial Vault Microservice Gateway
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from typing import Optional
from ofcs.ledger import OFCSFinancialLedger
from ofcs.money import Money, USD, Currency, get_currency
from .router import Request
from .response import Response


def mount_ofcs_vault(app, ledger: Optional[OFCSFinancialLedger] = None):
    """
    Mounts turnkey enterprise banking and double-entry financial microservice
    endpoints into the Haven application.
    """
    active_ledger = ledger or OFCSFinancialLedger(ledger_name="vault_primary")

    @app.post("/vault/accounts")
    def create_account(req: Request) -> Response:
        """Opens a new audited double-entry financial account."""
        body = req.json or {}
        acc_id = body.get("account_id")
        curr_str = body.get("currency", "USD")
        initial_val = body.get("initial_balance", "0.00")

        if not acc_id:
            return Response.error("Missing 'account_id' in request body", 400)

        curr = get_currency(curr_str) or USD
        acc = active_ledger.create_account(acc_id, currency=curr, initial_balance=initial_val)
        return Response.json({
            "status": "CREATED",
            "account_id": acc.account_id,
            "currency": acc.currency.code,
            "balance": str(acc.balance.amount)
        }, status_code=201)

    @app.get("/vault/accounts/{account_id}")
    def get_account_balance(req: Request) -> Response:
        """Retrieves verified balance for an account."""
        acc_id = req.path_params.get("account_id")
        if acc_id not in active_ledger.accounts:
            return Response.not_found(f"Account '{acc_id}' not found in vault")

        acc = active_ledger.accounts[acc_id]
        return Response.json({
            "account_id": acc.account_id,
            "currency": acc.currency.code,
            "balance": str(acc.balance.amount),
            "status": acc.status
        })

    @app.post("/vault/transfers")
    def execute_transfer(req: Request) -> Response:
        """Executes an atomic double-entry transfer enforcing Invariant 1 (Debits == Credits)."""
        body = req.json or {}
        from_id = body.get("from_account")
        to_id = body.get("to_account")
        amount_str = body.get("amount")
        desc = body.get("description", "Transfer")

        if not (from_id and to_id and amount_str):
            return Response.error("Parameters 'from_account', 'to_account', and 'amount' required", 400)

        if from_id not in active_ledger.accounts:
            return Response.not_found(f"Source account '{from_id}' not found")
        if to_id not in active_ledger.accounts:
            return Response.not_found(f"Destination account '{to_id}' not found")

        acc_from = active_ledger.accounts[from_id]
        curr = acc_from.currency
        money = Money(amount_str, curr)
        try:
            res = active_ledger.transfer(from_id, to_id, money, memo=desc)
            return Response.json({
                "status": "SUCCESS",
                "tx_id": res["tx_id"],
                "amount": str(money.amount),
                "currency": curr.code,
                "block_height": res["block_height"],
                "record_hash": res["record_hash"]
            })
        except Exception as e:
            return Response.error(f"Transfer Invariant Violation: {str(e)}", 400)

    @app.get("/vault/audit")
    def get_audit_trail(req: Request) -> Response:
        """Returns the tamper-evident audit ledger entries."""
        entries = [t.to_dict() for t in active_ledger.transactions]
        return Response.json({
            "ledger_name": active_ledger.ledger_name,
            "total_blocks": len(entries),
            "head_hash": active_ledger.block_hashes[-1],
            "verified": active_ledger.verify_ledger_chain(),
            "blocks": entries
        })

    return active_ledger
