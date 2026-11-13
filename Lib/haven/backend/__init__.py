"""
Haven Backend Framework v2.0.0
High-Performance, Multi-Threaded Microservices & ODCS/OFCS Native Server.
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from .response import Response, HavenJSONEncoder
from .router import Request, RouteEntry, Router
from .middleware import (
    Middleware,
    CORSMiddleware,
    ContinuityAuditMiddleware,
    RateLimiterMiddleware
)
from .server import HavenHTTPHandler, HavenServer, HavenApp
from .odcs_endpoints import register_continuity_endpoints
from .docs import build_openapi_spec, generate_interactive_docs_html
from .client import TestClient, TestResponse
from .orm import DurableModel, Field
from .auth import APIKeyAuthMiddleware, BearerAuthMiddleware, require_auth
from .tasks import BackgroundTaskPool
from .vault import mount_ofcs_vault

__all__ = [
    "Response",
    "HavenJSONEncoder",
    "Request",
    "RouteEntry",
    "Router",
    "Middleware",
    "CORSMiddleware",
    "ContinuityAuditMiddleware",
    "RateLimiterMiddleware",
    "HavenHTTPHandler",
    "HavenServer",
    "HavenApp",
    "register_continuity_endpoints",
    "build_openapi_spec",
    "generate_interactive_docs_html",
    "TestClient",
    "TestResponse",
    "DurableModel",
    "Field",
    "APIKeyAuthMiddleware",
    "BearerAuthMiddleware",
    "require_auth",
    "BackgroundTaskPool",
    "mount_ofcs_vault",
]
