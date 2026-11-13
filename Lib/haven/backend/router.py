"""
Haven Backend Framework - Request & Declarative Routing System
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlparse
from .response import Response


class Request:
    """Represents an incoming HTTP request in the Haven backend."""
    def __init__(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, List[str]]] = None,
        path_params: Optional[Dict[str, str]] = None,
        body_bytes: bytes = b"",
        client_address: Optional[Tuple[str, int]] = None
    ):
        self.method = method.upper()
        self.path = path
        self.headers = headers or {}
        self.query_params = query_params or {}
        self.path_params = path_params or {}
        self.body_bytes = body_bytes
        self.client_address = client_address
        self._json_cache: Optional[Any] = None

    @property
    def text(self) -> str:
        return self.body_bytes.decode("utf-8", errors="replace")

    @property
    def json(self) -> Any:
        if self._json_cache is None:
            if not self.body_bytes:
                self._json_cache = {}
            else:
                self._json_cache = json.loads(self.text)
        return self._json_cache

    def get_query(self, key: str, default: Optional[str] = None) -> Optional[str]:
        vals = self.query_params.get(key, [])
        return vals[0] if vals else default

    def get_header(self, key: str, default: Optional[str] = None) -> Optional[str]:
        # Case-insensitive header lookup
        k_lower = key.lower()
        for k, v in self.headers.items():
            if k.lower() == k_lower:
                return v
        return default

    def __repr__(self) -> str:
        return f"Request({self.method} {self.path})"


class RouteEntry:
    """Compiled route pattern with regex matcher."""
    def __init__(self, method: str, path_pattern: str, handler: Callable):
        self.method = method.upper()
        self.path_pattern = path_pattern
        self.handler = handler

        # Compile path regex for /{param} tokens
        # e.g., /api/accounts/{account_id}/tx -> ^/api/accounts/(?P<account_id>[^/]+)/tx$
        regex_pattern = re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', r'(?P<\1>[^/]+)', path_pattern)
        self.regex = re.compile(f"^{regex_pattern}$")

    def match(self, method: str, path: str) -> Optional[Dict[str, str]]:
        if self.method != "*" and self.method != method.upper():
            return None
        m = self.regex.match(path)
        if m:
            return m.groupdict()
        return None


class Router:
    """Declarative Route Dispatcher for Haven applications."""
    def __init__(self):
        self.routes: List[RouteEntry] = []

    def add_route(self, method: str, path: str, handler: Callable):
        self.routes.append(RouteEntry(method, path, handler))

    def get(self, path: str):
        def decorator(fn: Callable):
            self.add_route("GET", path, fn)
            return fn
        return decorator

    def post(self, path: str):
        def decorator(fn: Callable):
            self.add_route("POST", path, fn)
            return fn
        return decorator

    def put(self, path: str):
        def decorator(fn: Callable):
            self.add_route("PUT", path, fn)
            return fn
        return decorator

    def delete(self, path: str):
        def decorator(fn: Callable):
            self.add_route("DELETE", path, fn)
            return fn
        return decorator

    def patch(self, path: str):
        def decorator(fn: Callable):
            self.add_route("PATCH", path, fn)
            return fn
        return decorator

    def match(self, method: str, path: str) -> Optional[Tuple[Callable, Dict[str, str]]]:
        for entry in self.routes:
            params = entry.match(method, path)
            if params is not None:
                return entry.handler, params
        return None
