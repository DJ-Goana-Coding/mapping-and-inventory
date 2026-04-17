#!/usr/bin/env python3
"""
🛰️ /v1/ingest — Physical-Harvest HTTP endpoint.

Exposes a small, dependency-free HTTP server (stdlib only) that receives
telemetry packets from the S10 and Oppo-Node and routes them into
:class:`ingestion.omni_harvest.physical_harvest.PhysicalHarvest`.

Accepts ``POST /v1/ingest`` with a JSON body of the shape::

    {
      "source": "oppo-node" | "s10",
      "kind":   "hardware.json" | "assets.json",
      "data":   { ... }
    }

On success responds ``200`` with the telemetry record.  Malformed JSON
yields ``400`` and unknown routes yield ``404``.  A ``GET /health``
helper returns subsystem status for liveness probing.

Security notes
--------------
The server ships with **no authentication** — it is intended to run
behind a trusted network boundary (a reverse proxy, a WireGuard tunnel,
or bound to loopback only).  The CLI defaults to ``127.0.0.1`` to
prevent accidental exposure; explicitly passing ``--ingest-host
0.0.0.0`` is required for network-reachable deployments, and such
deployments MUST be fronted by an authenticating proxy.
"""

from __future__ import annotations

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, Optional, Tuple

from ingestion.omni_harvest.physical_harvest import PhysicalHarvest, TelemetryError

log = logging.getLogger(__name__)

INGEST_PATH = "/v1/ingest"
HEALTH_PATH = "/health"

# Internal handler / server factory so tests can spin up a real ephemeral
# HTTP server and exercise the wire protocol end-to-end.


def create_ingest_app(
    harvester: Optional[PhysicalHarvest] = None,
) -> Tuple[Callable[..., BaseHTTPRequestHandler], PhysicalHarvest]:
    """Build a ``BaseHTTPRequestHandler`` bound to *harvester*.

    Returns the handler class and the live ``PhysicalHarvest`` so the
    caller can introspect the ingested telemetry.
    """
    harvester = harvester or PhysicalHarvest()

    class IngestHandler(BaseHTTPRequestHandler):
        server_version = "OmniHarvestIngest/1.0"

        # Silence default stderr access logging (tests + daemons).
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            log.debug("ingest %s - %s", self.address_string(), format % args)

        # --- helpers ----------------------------------------------------
        def _send_json(self, status: int, body: Dict[str, Any]) -> None:
            payload = json.dumps(body).encode("utf-8")
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
        def do_POST(self) -> None:  # noqa: N802 - stdlib handler
            if self.path != INGEST_PATH:
                self._send_json(404, {"error": f"unknown route {self.path}"})
                return
            try:
                payload = self._read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": f"invalid JSON: {exc}"})
                return
            try:
                record = harvester.process_telemetry(payload)
            except TelemetryError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            except Exception as exc:  # pragma: no cover - defensive
                log.exception("ingest failed")
                self._send_json(500, {"error": str(exc)})
                return
            self._send_json(200, {"ok": True, "record": record})

        def do_GET(self) -> None:  # noqa: N802
            if self.path == HEALTH_PATH:
                self._send_json(200, {"ok": True, "status": harvester.status()})
                return
            self._send_json(404, {"error": f"unknown route {self.path}"})

    return IngestHandler, harvester


class IngestServer:
    """Threaded wrapper around an ``HTTPServer`` for ``/v1/ingest``."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        *,
        harvester: Optional[PhysicalHarvest] = None,
    ) -> None:
        handler_cls, self.harvester = create_ingest_app(harvester)
        self._server = HTTPServer((host, port), handler_cls)
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Address
    # ------------------------------------------------------------------

    @property
    def host(self) -> str:
        return self._server.server_address[0]

    @property
    def port(self) -> int:
        return self._server.server_address[1]

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._server.serve_forever, name="ingest-server", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)
        self._thread = None

    def __enter__(self) -> "IngestServer":
        self.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.stop()
