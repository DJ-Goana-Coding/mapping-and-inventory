#!/usr/bin/env python3
"""
🛰️ THE PHYSICAL HARVEST — WebSocket telemetry listener.

Parses ``hardware.json`` and ``assets.json`` payloads streamed from the
Oppo-Node (Librarian) and Samsung S10 (Field Uplink) into the real-time
Hardware Inventory.  The WebSocket transport is pluggable so tests can
feed synthetic payloads without opening a socket.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from inventory.asset_vault import AssetVault
from inventory.hardware_nodes import HardwareInventory

# Accepted telemetry sources.
SUPPORTED_SOURCES = ("oppo-node", "s10")

# Expected payload kinds.
KIND_HARDWARE = "hardware.json"
KIND_ASSETS = "assets.json"
SUPPORTED_KINDS = (KIND_HARDWARE, KIND_ASSETS)


class TelemetryError(ValueError):
    """Raised when a telemetry payload is malformed."""


class PhysicalHarvest:
    """WebSocket-driven ingest for the physical fleet telemetry."""

    def __init__(
        self,
        *,
        hardware_inventory: Optional[HardwareInventory] = None,
        asset_vault: Optional[AssetVault] = None,
        websocket_factory: Optional[Callable[[str], Any]] = None,
    ) -> None:
        self.hardware = hardware_inventory or HardwareInventory()
        self.assets = asset_vault or AssetVault()
        self._websocket_factory = websocket_factory
        self._telemetry_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Telemetry parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise(payload: Any) -> Dict[str, Any]:
        if isinstance(payload, (bytes, bytearray)):
            payload = payload.decode("utf-8")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError as exc:  # pragma: no cover - exercised in tests
                raise TelemetryError(f"Invalid JSON telemetry: {exc}") from exc
        if not isinstance(payload, dict):
            raise TelemetryError("Telemetry payload must be a JSON object")
        return payload

    def process_telemetry(self, payload: Any) -> Dict[str, Any]:
        """Process a single telemetry packet and update the inventory.

        The packet shape is::

            {
              "source": "oppo-node" | "s10",
              "kind":   "hardware.json" | "assets.json",
              "data":   { ... }
            }
        """
        packet = self._normalise(payload)

        source = str(packet.get("source", "")).lower()
        kind = packet.get("kind")
        data = packet.get("data")

        if source not in SUPPORTED_SOURCES:
            raise TelemetryError(
                f"Unsupported telemetry source {source!r}; expected one of {SUPPORTED_SOURCES}"
            )
        if kind not in SUPPORTED_KINDS:
            raise TelemetryError(
                f"Unsupported telemetry kind {kind!r}; expected one of {SUPPORTED_KINDS}"
            )
        if not isinstance(data, dict):
            raise TelemetryError("Telemetry 'data' must be a JSON object")

        if kind == KIND_HARDWARE:
            updates = self._apply_hardware(source, data)
        else:
            updates = self._apply_assets(source, data)

        record = {
            "source": source,
            "kind": kind,
            "updates": updates,
            "received_at": datetime.now(timezone.utc).isoformat(),
        }
        self._telemetry_log.append(record)
        return record

    # ------------------------------------------------------------------
    # hardware.json / assets.json appliers
    # ------------------------------------------------------------------

    def _apply_hardware(self, source: str, data: Dict[str, Any]) -> List[str]:
        """Upsert hardware-node definitions from a ``hardware.json`` packet."""
        nodes = data.get("nodes") or data  # allow {"nodes": {...}} or flat
        if not isinstance(nodes, dict):
            raise TelemetryError("hardware.json 'nodes' must be a JSON object")

        touched: List[str] = []
        for node_id, definition in nodes.items():
            if not isinstance(definition, dict):
                continue
            definition = dict(definition)
            definition.setdefault("source", source)
            try:
                self.hardware.get_node(node_id)
                # Exists: merge new fields into the existing node via
                # the public ``update_node`` API.
                self.hardware.update_node(node_id, definition)
            except KeyError:
                self.hardware.add_node(node_id, definition)
            touched.append(node_id)
        return touched

    def _apply_assets(self, source: str, data: Dict[str, Any]) -> List[str]:
        """Register assets from an ``assets.json`` packet into the vault."""
        assets = data.get("assets") or data
        if isinstance(assets, dict):
            iterable: Iterable[Any] = assets.values()
        elif isinstance(assets, list):
            iterable = assets
        else:
            raise TelemetryError("assets.json 'assets' must be a list or object")

        touched: List[str] = []
        for entry in iterable:
            if not isinstance(entry, dict):
                continue
            asset_id = entry.get("id") or entry.get("asset_id") or entry.get("name")
            if not asset_id:
                continue
            record = dict(entry)
            record.setdefault("source", source)
            self._register_asset(asset_id, record)
            touched.append(str(asset_id))
        return touched

    def _register_asset(self, asset_id: str, record: Dict[str, Any]) -> None:
        """Register or update an asset on the underlying AssetVault.

        Uses ``register`` / ``add_asset`` / ``upsert`` if available, and
        otherwise falls back to an internal cache so telemetry never
        silently disappears.
        """
        vault = self.assets
        for method in ("upsert_asset", "register_asset", "add_asset", "register", "upsert"):
            fn = getattr(vault, method, None)
            if callable(fn):
                try:
                    fn(asset_id, record)
                    return
                except TypeError:
                    try:
                        fn(record)
                        return
                    except Exception:  # pragma: no cover - defensive
                        continue
        # Fallback: stash on the vault instance so nothing is lost.
        cache = getattr(vault, "_omni_harvest_cache", None)
        if cache is None:
            cache = {}
            setattr(vault, "_omni_harvest_cache", cache)
        cache[asset_id] = record

    # ------------------------------------------------------------------
    # WebSocket listener
    # ------------------------------------------------------------------

    def listen(
        self,
        url: str,
        *,
        max_messages: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Open a WebSocket connection and stream telemetry packets.

        A ``websocket_factory`` must have been provided at construction
        time — this keeps the module import-time free of WebSocket
        dependencies and testable offline.  The factory must return an
        iterable of raw messages.
        """
        if self._websocket_factory is None:
            raise RuntimeError(
                "No websocket_factory configured; cannot open WebSocket listener"
            )
        stream = self._websocket_factory(url)
        processed: List[Dict[str, Any]] = []
        for i, message in enumerate(stream):
            if max_messages is not None and i >= max_messages:
                break
            processed.append(self.process_telemetry(message))
        return processed

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def telemetry_log(self) -> List[Dict[str, Any]]:
        return list(self._telemetry_log)

    def status(self) -> Dict[str, Any]:
        return {
            "total_packets": len(self._telemetry_log),
            "hardware_nodes": len(self.hardware.list_nodes()),
            "supported_sources": list(SUPPORTED_SOURCES),
            "supported_kinds": list(SUPPORTED_KINDS),
            "websocket_ready": self._websocket_factory is not None,
        }
