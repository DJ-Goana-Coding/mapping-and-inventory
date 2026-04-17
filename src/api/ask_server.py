#!/usr/bin/env python3
"""
🧠 /v1/ask — T.I.A. cross-domain query endpoint.

Exposes a small, dependency-free HTTP server that fronts
:class:`src.query.rag_engine.RAGQueryEngine`.

Routes
------
``POST /v1/ask`` — body::

    {
      "query": "Compare Partition_01 logic with today's Vortex trade logs",
      "domains": ["partition_01", "vortex"],   // optional
      "top_k": 5                                // optional
    }

When ``domains`` is provided the engine performs cross-domain inference
and returns ``{"ok": true, "answer": <CrossDomainAnswer>}``.  When
omitted, a flat top-*k* retrieval is returned: ``{"ok": true, "hits":
[...]}``.

``GET /health`` returns engine status for liveness probing.

Security note
-------------
Like ``/v1/ingest``, this server ships with **no authentication**.  It
is meant to run on loopback or behind a trusted reverse proxy.
"""

from __future__ import annotations

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, Optional, Tuple

from src.query.rag_engine import RAGQueryEngine

log = logging.getLogger(__name__)

ASK_PATH = "/v1/ask"
HEALTH_PATH = "/health"


def create_ask_app(
    engine: Optional[RAGQueryEngine] = None,
) -> Tuple[Callable[..., BaseHTTPRequestHandler], RAGQueryEngine]:
    """Build a ``BaseHTTPRequestHandler`` bound to *engine*."""
    engine = engine if engine is not None else RAGQueryEngine()

    class AskHandler(BaseHTTPRequestHandler):
        server_version = "OmniReceptionAsk/1.0"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            log.debug("ask %s - %s", self.address_string(), format % args)

        # --- helpers ----------------------------------------------------
        def _send_json(self, status: int, body: Dict[str, Any]) -> None:
            payload = json.dumps(body, default=str).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def _read_json(self) -> Any:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0:
                raise ValueError("empty request body")
            raw = self.rfile.read(length)
            return json.loads(raw.decode("utf-8"))

        # --- routes -----------------------------------------------------
        def do_POST(self) -> None:  # noqa: N802
            if self.path != ASK_PATH:
                self._send_json(404, {"error": f"unknown route {self.path}"})
                return
            try:
                payload = self._read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": f"invalid JSON: {exc}"})
                return
            if not isinstance(payload, dict):
                self._send_json(400, {"error": "request body must be a JSON object"})
                return

            query = payload.get("query")
            if not isinstance(query, str) or not query.strip():
                self._send_json(400, {"error": "missing 'query' string"})
                return

            top_k_raw = payload.get("top_k", 5)
            try:
                top_k = max(1, int(top_k_raw))
            except (TypeError, ValueError):
                self._send_json(400, {"error": "'top_k' must be an integer"})
                return

            domains = payload.get("domains")
            try:
                if domains:
                    if not isinstance(domains, list) or not all(
                        isinstance(d, str) for d in domains
                    ):
                        self._send_json(
                            400, {"error": "'domains' must be a list of strings"}
                        )
                        return
                    answer = engine.cross_domain_inference(
                        query, domains=domains, top_k=top_k
                    )
                    self._send_json(200, {"ok": True, "answer": answer.as_dict()})
                else:
                    hits = engine.retrieve(query, top_k=top_k)
                    self._send_json(200, {"ok": True, "hits": hits})
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
            except Exception as exc:  # pragma: no cover - defensive
                log.exception("ask failed")
                self._send_json(500, {"error": str(exc)})

        def do_GET(self) -> None:  # noqa: N802
            if self.path == HEALTH_PATH:
                self._send_json(200, {"ok": True, "status": engine.status()})
                return
            self._send_json(404, {"error": f"unknown route {self.path}"})

    return AskHandler, engine


class AskServer:
    """Threaded wrapper around an ``HTTPServer`` for ``/v1/ask``."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        *,
        engine: Optional[RAGQueryEngine] = None,
    ) -> None:
        handler_cls, self.engine = create_ask_app(engine)
        self._server = HTTPServer((host, port), handler_cls)
        self._thread: Optional[threading.Thread] = None

    @property
    def host(self) -> str:
        return self._server.server_address[0]

    @property
    def port(self) -> int:
        return self._server.server_address[1]

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._server.serve_forever, name="ask-server", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)
        self._thread = None

    def __enter__(self) -> "AskServer":
        self.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.stop()


__all__ = ["AskServer", "create_ask_app", "ASK_PATH"]
