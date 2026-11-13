"""
Haven Backend Framework - HTTP Response System
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import json
from decimal import Decimal
from typing import Any, Dict, Optional, Union


class HavenJSONEncoder(json.JSONEncoder):
    """Encodes Decimal, Money, DurableRecord, and Currency objects deterministically."""
    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return str(o)
        if hasattr(o, "to_dict") and callable(o.to_dict):
            return o.to_dict()
        if hasattr(o, "odcs_dict") and callable(o.odcs_dict):
            return o.odcs_dict()
        if hasattr(o, "name") and callable(o.name):
            return o.name()
        return super().default(o)


class Response:
    """HTTP Response builder for Haven Backend services."""
    def __init__(
        self,
        body: Union[str, bytes] = "",
        status_code: int = 200,
        content_type: str = "text/plain; charset=utf-8",
        headers: Optional[Dict[str, str]] = None
    ):
        self.status_code = status_code
        self.headers = headers or {}
        self.headers.setdefault("Content-Type", content_type)
        self.headers.setdefault("Server", "Haven-Backend/1.0.0 (ODCS-Native)")

        if isinstance(body, str):
            self.body_bytes = body.encode("utf-8")
        elif isinstance(body, bytes):
            self.body_bytes = body
        else:
            self.body_bytes = str(body).encode("utf-8")

        self.headers["Content-Length"] = str(len(self.body_bytes))

    @classmethod
    def json(cls, data: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None) -> "Response":
        """Constructs a deterministic JSON response."""
        encoded = json.dumps(data, cls=HavenJSONEncoder, indent=2, sort_keys=True)
        return cls(
            body=encoded,
            status_code=status_code,
            content_type="application/json; charset=utf-8",
            headers=headers
        )

    @classmethod
    def html(cls, html_content: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None) -> "Response":
        """Constructs an HTML response."""
        return cls(
            body=html_content,
            status_code=status_code,
            content_type="text/html; charset=utf-8",
            headers=headers
        )

    @classmethod
    def ok(cls, message: str = "OK", data: Optional[Any] = None) -> "Response":
        """Constructs a standard 200 OK JSON response."""
        payload = {"status": "success", "message": message}
        if data is not None:
            payload["data"] = data
        return cls.json(payload, status_code=200)

    @classmethod
    def error(cls, message: str, status_code: int = 400, error_code: str = "ERROR") -> "Response":
        """Constructs a standard error JSON response."""
        payload = {
            "status": "error",
            "error_code": error_code,
            "message": message
        }
        return cls.json(payload, status_code=status_code)

    @classmethod
    def not_found(cls, message: str = "Resource not found") -> "Response":
        return cls.error(message, status_code=404, error_code="NOT_FOUND")

    @classmethod
    def unauthorized(cls, message: str = "Authentication required") -> "Response":
        return cls.error(message, status_code=401, error_code="UNAUTHORIZED")
