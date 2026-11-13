"""
Haven Backend Framework - Enterprise Middleware Pipeline
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import time
import hashlib
from typing import Callable, Dict, List, Optional
from .router import Request
from .response import Response


class Middleware:
    """Base middleware processor."""
    def process_request(self, request: Request) -> Optional[Response]:
        """Runs before handler. Return a Response to short-circuit, or None to continue."""
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        """Runs after handler. Can inspect or modify response."""
        return response


class CORSMiddleware(Middleware):
    """Enables Cross-Origin Resource Sharing for modern browser frontends."""
    def __init__(
        self,
        allow_origins: str = "*",
        allow_methods: str = "GET, POST, PUT, DELETE, OPTIONS, PATCH",
        allow_headers: str = "Content-Type, Authorization, X-Requested-With, X-Haven-Signature",
        max_age: int = 86400
    ):
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.max_age = str(max_age)

    def process_request(self, request: Request) -> Optional[Response]:
        if request.method == "OPTIONS":
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": self.allow_origins,
                    "Access-Control-Allow-Methods": self.allow_methods,
                    "Access-Control-Allow-Headers": self.allow_headers,
                    "Access-Control-Max-Age": self.max_age,
                }
            )
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        response.headers.setdefault("Access-Control-Allow-Origin", self.allow_origins)
        response.headers.setdefault("Access-Control-Allow-Methods", self.allow_methods)
        response.headers.setdefault("Access-Control-Allow-Headers", self.allow_headers)
        return response


class ContinuityAuditMiddleware(Middleware):
    """
    ODCS Invariant: Cryptographically seals every incoming transaction
    into the local append-only ledger before responding to clients.
    """
    def __init__(self, ledger=None):
        self.ledger = ledger

    def process_response(self, request: Request, response: Response) -> Response:
        from haven.continuity import _GLOBAL_LEDGER
        active_ledger = self.ledger or _GLOBAL_LEDGER

        # Compute deterministic interaction fingerprint
        interaction_payload = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "client": str(request.client_address),
            "timestamp": time.time(),
            "req_len": len(request.body_bytes),
            "resp_len": len(response.body_bytes)
        }

        # Checkpoint into ledger
        entry = active_ledger.commit(interaction_payload, alias=f"http_{request.method}_{request.path}")
        response.headers["X-Haven-Continuity-Receipt"] = entry.entry_hash
        response.headers["X-Haven-Block-Height"] = str(entry.index)
        return response


class RateLimiterMiddleware(Middleware):
    """Simple sliding-window rate limiter per client IP."""
    def __init__(self, max_requests_per_minute: int = 600):
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60.0
        self.history: Dict[str, List[float]] = {}

    def process_request(self, request: Request) -> Optional[Response]:
        client_ip = request.client_address[0] if request.client_address else "unknown"
        now = time.time()
        cutoff = now - self.window_seconds

        client_times = self.history.get(client_ip, [])
        client_times = [t for t in client_times if t > cutoff]
        client_times.append(now)
        self.history[client_ip] = client_times

        if len(client_times) > self.max_requests:
            return Response.error("Rate limit exceeded. Too many requests.", status_code=429, error_code="RATE_LIMITED")
        return None

