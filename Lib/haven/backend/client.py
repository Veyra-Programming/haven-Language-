"""
Haven Backend Framework - In-Memory Fast Test Client
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import json
from urllib.parse import urlparse, parse_qs
from typing import Any, Dict, Optional, Union
from .response import Response
from .router import Request


class TestResponse:
    """Encapsulates test response details for assertions."""
    def __init__(self, response: Response):
        self.status_code = response.status_code
        self.headers = response.headers
        self.body_bytes = response.body_bytes

    @property
    def text(self) -> str:
        return self.body_bytes.decode("utf-8", errors="replace")

    @property
    def json(self) -> Any:
        return json.loads(self.text)

    def __repr__(self) -> str:
        return f"<TestResponse [{self.status_code}]>"


class TestClient:
    """
    In-Memory Test Client for Haven Backend Microservices.
    Allows zero-port, instantaneous unit and integration testing of API endpoints.
    """
    def __init__(self, app: Any):
        self.app = app

    def request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[Union[str, bytes, dict]] = None
    ) -> TestResponse:
        parsed = urlparse(path)
        clean_path = parsed.path
        raw_query = parse_qs(parsed.query)

        if query_params:
            for k, v in query_params.items():
                raw_query[k] = [str(v)]

        body_bytes = b""
        req_headers = headers.copy() if headers else {}

        if body is not None:
            if isinstance(body, dict):
                body_bytes = json.dumps(body).encode("utf-8")
                req_headers.setdefault("Content-Type", "application/json")
            elif isinstance(body, str):
                body_bytes = body.encode("utf-8")
            elif isinstance(body, bytes):
                body_bytes = body

        req_headers.setdefault("Content-Length", str(len(body_bytes)))

        req = Request(
            method=method.upper(),
            path=clean_path,
            headers=req_headers,
            query_params=raw_query,
            body_bytes=body_bytes,
            client_address=("127.0.0.1", 54321)
        )

        # 1. Pre-processing Middlewares
        middlewares = getattr(self.app, "custom_middlewares", [])
        response: Optional[Response] = None

        for mw in middlewares:
            try:
                resp = mw.process_request(req)
                if resp is not None:
                    response = resp
                    break
            except Exception as e:
                response = Response.error(f"Middleware Error: {str(e)}", 500)
                break

        # 2. Router Execution
        if response is None:
            router = getattr(self.app, "router", None)
            if router:
                matched = router.match(req.method, req.path)
                if matched:
                    handler, path_params = matched
                    req.path_params = path_params
                    try:
                        res = handler(req)
                        if isinstance(res, Response):
                            response = res
                        elif isinstance(res, (dict, list)):
                            response = Response.json(res)
                        elif isinstance(res, str):
                            response = Response.text(res)
                        elif res is None:
                            response = Response.ok()
                        else:
                            response = Response.json(res)
                    except Exception as e:
                        response = Response.error(f"Handler Error: {str(e)}", 500)
                else:
                    response = Response.not_found(f"Route '{req.method} {req.path}' not found")
            else:
                response = Response.error("No router configured", 500)

        # 3. Post-processing Middlewares
        for mw in reversed(middlewares):
            try:
                response = mw.process_response(req, response)
            except Exception:
                pass

        return TestResponse(response)

    def get(self, path: str, headers: Optional[Dict[str, str]] = None, query: Optional[Dict[str, Any]] = None) -> TestResponse:
        return self.request("GET", path, headers=headers, query_params=query)

    def post(self, path: str, json: Optional[Any] = None, data: Optional[Union[str, bytes]] = None, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        body = json if json is not None else data
        return self.request("POST", path, headers=headers, body=body)

    def put(self, path: str, json: Optional[Any] = None, data: Optional[Union[str, bytes]] = None, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        body = json if json is not None else data
        return self.request("PUT", path, headers=headers, body=body)

    def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        return self.request("DELETE", path, headers=headers)

    def patch(self, path: str, json: Optional[Any] = None, data: Optional[Union[str, bytes]] = None, headers: Optional[Dict[str, str]] = None) -> TestResponse:
        body = json if json is not None else data
        return self.request("PATCH", path, headers=headers, body=body)
