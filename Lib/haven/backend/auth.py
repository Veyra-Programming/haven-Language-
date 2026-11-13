"""
Haven Backend Framework - Authentication & Authorization Middleware
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from typing import Any, Callable, Dict, List, Optional, Set
from .middleware import Middleware
from .router import Request
from .response import Response


class APIKeyAuthMiddleware(Middleware):
    """Verifies incoming requests against authorized API keys."""
    def __init__(self, api_keys: List[str], header_name: str = "X-API-Key", exclude_paths: Optional[Set[str]] = None):
        self.api_keys = set(api_keys)
        self.header_name = header_name
        self.exclude_paths = exclude_paths or {"/docs", "/openapi.json", "/odcs/health"}

    def process_request(self, request: Request) -> Optional[Response]:
        if request.path in self.exclude_paths:
            return None

        key = request.get_header(self.header_name)
        if not key or key not in self.api_keys:
            return Response.unauthorized(f"Missing or invalid API key in header '{self.header_name}'")

        request.auth = {"type": "api_key", "key": key}
        return None


class BearerAuthMiddleware(Middleware):
    """Verifies Bearer token in Authorization header."""
    def __init__(self, valid_tokens: List[str], exclude_paths: Optional[Set[str]] = None):
        self.valid_tokens = set(valid_tokens)
        self.exclude_paths = exclude_paths or {"/docs", "/openapi.json", "/odcs/health"}

    def process_request(self, request: Request) -> Optional[Response]:
        if request.path in self.exclude_paths:
            return None

        auth_header = request.get_header("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response.unauthorized("Missing or malformed Authorization header (expected 'Bearer <token>')")

        token = auth_header[7:].strip()
        if token not in self.valid_tokens:
            return Response.unauthorized("Invalid or expired Bearer token")

        request.auth = {"type": "bearer", "token": token, "user": "authenticated_client"}
        return None


def require_auth(handler: Callable) -> Callable:
    """Decorator ensuring request has valid authentication context."""
    def wrapper(req: Request, *args, **kwargs):
        if not getattr(req, "auth", None):
            return Response.unauthorized("Authentication required for this endpoint")
        return handler(req, *args, **kwargs)
    wrapper.__doc__ = handler.__doc__
    return wrapper
