"""
Haven Backend Framework - Standard ODCS & OFCS Built-in Endpoints
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from typing import Any, Dict
from .router import Request, Router
from .response import Response
from haven.continuity import _GLOBAL_LEDGER
from ofcs.ledger import _GLOBAL_FINANCIAL_LEDGER


def register_continuity_endpoints(router: Router):
    """Mounts standard ODCS and OFCS REST verification routes."""

    @router.get("/odcs/health")
    def odcs_health(req: Request) -> Response:
        """Returns node health, block height, and continuity verification status."""
        is_valid = _GLOBAL_LEDGER.verify_integrity()
        return Response.json({
            "status": "HEALTHY" if is_valid else "CORRUPTED",
            "standard": "ODCS-1.0.0",
            "architecture_author": "Anirudha Puthraya",
            "ledger_name": _GLOBAL_LEDGER.name,
            "block_height": len(_GLOBAL_LEDGER.entries),
            "head_hash": _GLOBAL_LEDGER.head_hash,
            "integrity_verified": is_valid
        })

    @router.get("/odcs/ledger/blocks")
    def odcs_blocks(req: Request) -> Response:
        """Returns paginated blocks from the local continuity ledger."""
        limit_str = req.get_query("limit", "20")
        try:
            limit = min(int(limit_str), 100)
        except ValueError:
            limit = 20

        entries = [e.to_dict() for e in _GLOBAL_LEDGER.entries[-limit:]]
        return Response.json({
            "count": len(entries),
            "total_blocks": len(_GLOBAL_LEDGER.entries),
            "blocks": entries
        })

    @router.get("/ofcs/accounts")
    def ofcs_accounts(req: Request) -> Response:
        """Returns list of registered financial accounts in the OFCS ledger."""
        accts = [acct.to_dict() for acct in _GLOBAL_FINANCIAL_LEDGER.accounts.values()]
        return Response.json({
            "standard": "OFCS-1.0.0",
            "ledger_name": _GLOBAL_FINANCIAL_LEDGER.ledger_name,
            "accounts": accts
        })

    @router.get("/ofcs/accounts/{account_id}")
    def ofcs_account_detail(req: Request) -> Response:
        """Returns account details and exact decimal balance."""
        acct_id = req.path_params.get("account_id", "")
        if acct_id not in _GLOBAL_FINANCIAL_LEDGER.accounts:
            return Response.not_found(f"Account '{acct_id}' not found")
        acct = _GLOBAL_FINANCIAL_LEDGER.get_account(acct_id)
        return Response.json(acct.to_dict())
