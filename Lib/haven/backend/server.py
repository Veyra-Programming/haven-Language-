"""
Haven Backend Framework - High-Performance Multi-Threaded HTTP Server
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import http.server
import socketserver
import threading
import urllib.parse
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .router import Request, Router
from .response import Response
from .middleware import Middleware, CORSMiddleware, ContinuityAuditMiddleware, RateLimiterMiddleware
from .odcs_endpoints import register_continuity_endpoints


class HavenHTTPHandler(http.server.BaseHTTPRequestHandler):
    """Multi-threaded Request Handler dispatching to Haven Router and Middleware Pipeline."""
    server: 'HavenServer'

    def do_request(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        req = Request(
            method=self.command,
            path=path,
            headers=dict(self.headers),
            query_params=query,
            body_bytes=body,
            client_address=self.client_address
        )

        # 1. Execute middleware pre-processing
        response: Optional[Response] = None
        for mw in self.server.middlewares:
            try:
                resp = mw.process_request(req)
                if resp is not None:
                    response = resp
                    break
            except Exception as e:
                response = Response.error(f"Middleware Error: {str(e)}", 500)
                break

        # 2. Route matching and execution if not short-circuited
        if response is None:
            matched = self.server.router.match(req.method, req.path)
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
                        response = Response.no_content()
                    else:
                        response = Response.json(res)
                except Exception as e:
                    response = Response.error(f"Internal Server Error: {str(e)}", 500)
            else:
                response = Response.not_found(f"Route '{req.method} {req.path}' not found")

        # 3. Execute middleware post-processing (in reverse pipeline order)
        for mw in reversed(self.server.middlewares):
            try:
                response = mw.process_response(req, response)
            except Exception:
                pass

        # 4. Transmit HTTP response
        self.send_response(response.status_code)
        for k, v in response.headers.items():
            self.send_header(k, str(v))
        self.end_headers()
        self.wfile.write(response.body_bytes)

    def do_GET(self): self.do_request()
    def do_POST(self): self.do_request()
    def do_PUT(self): self.do_request()
    def do_DELETE(self): self.do_request()
    def do_PATCH(self): self.do_request()
    def do_OPTIONS(self): self.do_request()
    def do_HEAD(self): self.do_request()

    def log_message(self, format, *args):
        if getattr(self.server, "verbose", False):
            sys.stderr.write(f"[HavenHTTP] {self.address_string()} - {format % args}\n")


class HavenServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
    High-Performance Concurrent Multi-Threaded HTTP Server for Haven Backend Applications.
    """
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        router: Optional[Router] = None,
        verbose: bool = False
    ):
        self.host = host
        self.port = port
        self.router = router or Router()
        self.middlewares: List[Middleware] = []
        self.verbose = verbose
        self._thread: Optional[threading.Thread] = None
        super().__init__((host, port), HavenHTTPHandler)

    def use(self, middleware: Middleware) -> 'HavenServer':
        """Registers a middleware into the processing chain."""
        self.middlewares.append(middleware)
        return self

    def get(self, path: str):
        """Declarative GET route decorator."""
        return self.router.get(path)

    def post(self, path: str):
        """Declarative POST route decorator."""
        return self.router.post(path)

    def put(self, path: str):
        """Declarative PUT route decorator."""
        return self.router.put(path)

    def delete(self, path: str):
        """Declarative DELETE route decorator."""
        return self.router.delete(path)

    def patch(self, path: str):
        """Declarative PATCH route decorator."""
        return self.router.patch(path)

    def enable_odcs_endpoints(self) -> 'HavenServer':
        """Mounts standard ODCS and OFCS verification endpoints."""
        register_continuity_endpoints(self.router)
        return self

    def start(self, blocking: bool = True):
        """Starts the Haven HTTP Server."""
        if blocking:
            try:
                self.serve_forever()
            except KeyboardInterrupt:
                self.stop()
        else:
            self._thread = threading.Thread(target=self.serve_forever, daemon=True)
            self._thread.start()

    def stop(self):
        """Cleanly terminates the server."""
        self.shutdown()
        self.server_close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)


class HavenApp:
    """
    Enterprise Application Container for Haven Microservices and Web APIs.
    """
    def __init__(
        self,
        name: str = "HavenApplication",
        host: str = "127.0.0.1",
        port: int = 8080,
        cors: bool = True,
        continuity_audit: bool = True,
        rate_limit: int = 1200,
        enable_docs: bool = True
    ):
        self.name = name
        self.host = host
        self.port = port
        self.router = Router()
        self.server: Optional[HavenServer] = None
        self._cors = cors
        self._audit = continuity_audit
        self._rate_limit = rate_limit
        self._enable_docs = enable_docs
        self.custom_middlewares: List[Middleware] = []
        self._task_pool = None

    def with_port(self, port: int) -> 'HavenApp':
        self.port = port
        return self

    def with_host(self, host: str) -> 'HavenApp':
        self.host = host
        return self

    def with_cors(self, enable: bool = True) -> 'HavenApp':
        self._cors = enable
        return self

    def with_audit(self, enable: bool = True) -> 'HavenApp':
        self._audit = enable
        return self

    def with_rate_limit(self, max_requests: int) -> 'HavenApp':
        self._rate_limit = max_requests
        return self

    def with_docs(self, enable: bool = True) -> 'HavenApp':
        self._enable_docs = enable
        return self

    def with_api_key(self, *keys: str) -> 'HavenApp':
        from .auth import APIKeyAuthMiddleware
        self.use(APIKeyAuthMiddleware(list(keys)))
        return self

    def with_bearer_token(self, *tokens: str) -> 'HavenApp':
        from .auth import BearerAuthMiddleware
        self.use(BearerAuthMiddleware(list(tokens)))
        return self

    def use(self, middleware: Middleware) -> 'HavenApp':
        self.custom_middlewares.append(middleware)
        return self

    def get(self, path: str):
        return self.router.get(path)

    def post(self, path: str):
        return self.router.post(path)

    def put(self, path: str):
        return self.router.put(path)

    def delete(self, path: str):
        return self.router.delete(path)

    def patch(self, path: str):
        return self.router.patch(path)

    def enable_docs_endpoints(self, docs_path: str = "/docs", spec_path: str = "/openapi.json"):
        """Registers OpenAPI 3.0 specification and interactive dark-mode documentation."""
        from .docs import build_openapi_spec, generate_interactive_docs_html

        @self.router.get(spec_path)
        def get_spec(req: Request) -> Response:
            spec = build_openapi_spec(self.name, self.router)
            return Response.json(spec)

        @self.router.get(docs_path)
        def get_docs(req: Request) -> Response:
            html = generate_interactive_docs_html(self.name, spec_url=spec_path)
            return Response.html(html)

    def test_client(self):
        """Returns an In-Memory Test Client for zero-port unit testing."""
        from .client import TestClient
        if self._enable_docs:
            self.enable_docs_endpoints()
        return TestClient(self)

    def dispatch_task(self, func: Callable, *args, **kwargs):
        """Dispatches an asynchronous background task."""
        from .tasks import BackgroundTaskPool
        if self._task_pool is None:
            self._task_pool = BackgroundTaskPool()
        return self._task_pool.dispatch(func, *args, **kwargs)

    def mount_vault(self, ledger=None):
        """Mounts turnkey OFCS double-entry financial banking microservice."""
        from .vault import mount_ofcs_vault
        return mount_ofcs_vault(self, ledger=ledger)

    def run(self, blocking: bool = True, verbose: bool = False) -> HavenServer:
        if self._enable_docs:
            self.enable_docs_endpoints()

        self.server = HavenServer(
            host=self.host,
            port=self.port,
            router=self.router,
            verbose=verbose
        )

        # Standard middleware chain
        if self._cors:
            self.server.use(CORSMiddleware())
        if self._rate_limit > 0:
            self.server.use(RateLimiterMiddleware(max_requests_per_minute=self._rate_limit))
        for m in self.custom_middlewares:
            self.server.use(m)
        if self._audit:
            self.server.use(ContinuityAuditMiddleware())

        self.server.enable_odcs_endpoints()
        self.server.start(blocking=blocking)
        return self.server

    def stop(self):
        if self._task_pool:
            self._task_pool.shutdown()
        if self.server:
            self.server.stop()

