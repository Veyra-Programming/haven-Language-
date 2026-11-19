"""
Ani++ & Haven Real-Time Microservice & Web Engine (ani.net / haven.net)
Standard: Open Digital Continuity Standard (ODCS) Network Subsystem
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides a fast, zero-dependency declarative HTTP/REST Microservice router,
Server-Sent Events (SSE) streaming, Token-Bucket Rate Limiter, and
in-memory TestClient unified with the Haven Backend ecosystem.
"""

import re
import json
import time
import urllib.parse
from typing import Dict, List, Tuple, Callable, Any, Optional, Union

from haven.backend.response import Response
from haven.backend.router import Request
from haven.backend.client import TestClient, TestResponse


class RateLimiter:
    """Token-Bucket Rate Limiter for API endpoints."""

    def __init__(self, rate_per_second: float = 10.0, capacity: float = 20.0):
        self.rate = rate_per_second
        self.capacity = capacity
        self.buckets: Dict[str, Tuple[float, float]] = {}

    def allow(self, client_key: str = "default") -> bool:
        now = time.time()
        tokens, last_update = self.buckets.get(client_key, (self.capacity, now))
        elapsed = now - last_update
        tokens = min(self.capacity, tokens + elapsed * self.rate)
        if tokens >= 1.0:
            self.buckets[client_key] = (tokens - 1.0, now)
            return True
        self.buckets[client_key] = (tokens, now)
        return False


class MicroApp:
    """Declarative REST & Streaming Microservice Router."""

    def __init__(self, title: str = "Haven Microservice", cors: bool = True):
        self.title = title
        self.cors = cors
        # List of (method, regex_pattern, param_names, handler_fn)
        self.routes: List[Tuple[str, re.Pattern, List[str], Callable]] = []

    def route(self, path: str, methods: Optional[List[str]] = None):
        methods = [m.upper() for m in (methods or ["GET"])]
        param_names = re.findall(r"\{([a-zA-Z0-9_]+)\}", path)
        regex_path = "^" + re.sub(r"\{[a-zA-Z0-9_]+\}", r"([^/]+)", path) + "$"
        compiled_regex = re.compile(regex_path)

        def decorator(fn: Callable):
            for m in methods:
                self.routes.append((m, compiled_regex, param_names, fn))
            return fn
        return decorator

    def get(self, path: str):
        return self.route(path, methods=["GET"])

    def post(self, path: str):
        return self.route(path, methods=["POST"])

    def put(self, path: str):
        return self.route(path, methods=["PUT"])

    def delete(self, path: str):
        return self.route(path, methods=["DELETE"])

    def dispatch(self, request: Request) -> Response:
        # Handle CORS preflight
        if self.cors and request.method == "OPTIONS":
            return Response("", status_code=204, headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            })

        for method, pattern, param_names, handler in self.routes:
            if method == request.method:
                m = pattern.match(request.path)
                if m:
                    extracted_params = dict(zip(param_names, m.groups()))
                    request.path_params = extracted_params
                    try:
                        res = handler(request)
                        if isinstance(res, (dict, list)):
                            res = Response.json(res)
                        elif isinstance(res, str):
                            res = Response(res)
                        elif not isinstance(res, Response):
                            res = Response(str(res))
                        if self.cors:
                            res.headers["Access-Control-Allow-Origin"] = "*"
                        return res
                    except Exception as e:
                        return Response.json({"error": "InternalServerError", "message": str(e)}, status_code=500)

        return Response.json({"error": "NotFound", "path": request.path}, status_code=404)

    def test_client(self) -> "MicroTestClient":
        """Returns an in-memory client for testing endpoints without a network port."""
        return MicroTestClient(self)


class MicroTestClient:
    """Zero-port, high-speed in-memory HTTP client for testing MicroApps."""

    def __init__(self, app: MicroApp):
        self.app = app

    def request(
        self,
        method: str,
        url: str,
        json_data: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> TestResponse:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or "/"
        query = urllib.parse.parse_qs(parsed.query)
        headers = headers or {}
        body = b""
        if json_data is not None:
            body = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"

        req = Request(
            method=method,
            path=path,
            headers=headers,
            body_bytes=body,
            query_params=query
        )
        res = self.app.dispatch(req)
        return TestResponse(res)

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        return self.request("GET", url, headers=headers)

    def post(self, url: str, json: Any = None, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        return self.request("POST", url, json_data=json, headers=headers)

    def put(self, url: str, json: Any = None, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        return self.request("PUT", url, json_data=json, headers=headers)

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        return self.request("DELETE", url, headers=headers)


def sse_event(data: str, event: Optional[str] = None, event_id: Optional[str] = None) -> str:
    """Formats a message for Server-Sent Events (SSE)."""
    lines = []
    if event:
        lines.append(f"event: {event}")
    if event_id:
        lines.append(f"id: {event_id}")
    for part in data.splitlines():
        lines.append(f"data: {part}")
    lines.append("\n")
    return "\n".join(lines)
