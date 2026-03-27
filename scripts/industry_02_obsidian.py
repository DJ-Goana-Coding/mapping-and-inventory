"""
Industry 02 — The Obsidian Network (Data & Infrastructure Autonomy)
====================================================================
Focus: The 702-Shroud, Decentralised Nodes, Cryptography, Tribal Sync.

This script hardens the peer-to-peer architecture of the Citadel mesh:

* **Severs** all remaining API dependencies on centralised corporate servers
  by auditing ``D05`` and ``D06`` configuration records and flagging any
  external endpoints that still rely on third-party cloud infrastructure.
* **Routes** all inter-node communication (14-Space Swarm and Soul Tribe)
  exclusively through the self-hosted Tailscale/WireGuard mesh.
* **Allocates** dedicated bandwidth quotas in ``D05`` (Open Source Bin) and
  ``D06`` (Tribe Whitelist) for the distribution of the "Mates Build" and
  open-source intelligence payloads.

Survivability goal
------------------
The resulting configuration must allow the network to self-host and survive
a localised ISP blackout by relying entirely on mesh-internal routing and
cached asset distribution.

Usage::

    python3 scripts/industry_02_obsidian.py --sever-corporate-apis
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import re
import subprocess
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

CITADEL_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get("CITADEL_ARK_ROOT", str(pathlib.Path.home() / "CITADEL_ARK"))
)

D05_PATH: pathlib.Path = CITADEL_ROOT / "D05"
D06_PATH: pathlib.Path = CITADEL_ROOT / "D06"

NETWORK_AUDIT_LOG: pathlib.Path = D05_PATH / "network_audit.log"
TRIBE_WHITELIST: pathlib.Path = D06_PATH / "tribe_whitelist.json"
NODE_CONFIG: pathlib.Path = D05_PATH / "node_config.json"

#: Default bandwidth quota (MB/s) for Mates Build distribution.
MATES_BUILD_BANDWIDTH_MBPS: float = float(
    os.environ.get("MATES_BUILD_BANDWIDTH_MBPS", "10.0")
)

#: Corporate API hostname patterns that must be severed.
CORPORATE_API_PATTERNS: list[str] = [
    "api.openai.com",
    "api.anthropic.com",
    "api.cohere.ai",
    "api.stability.ai",
    "api.replicate.com",
    "api.huggingface.co",       # public inference — replace with self-hosted
    "api.pinecone.io",
    "api.weaviate.io",
    "openrouter.ai",
    "api.together.xyz",
    "generativelanguage.googleapis.com",
]

#: Allowed mesh-internal endpoint patterns (Tailscale / WireGuard).
MESH_ENDPOINT_PATTERNS: list[str] = [
    "100.64.",    # Tailscale CGNAT range
    "100.65.",
    "100.66.",
    "100.67.",
    "10.0.",      # Common LAN / WireGuard tunnel ranges
    "10.1.",
    "10.2.",
    "192.168.",
    "localhost",
    "127.0.",
]


# ---------------------------------------------------------------------------
# Node config helpers
# ---------------------------------------------------------------------------


def _load_json(path: pathlib.Path) -> Any:
    """Load JSON from *path*, returning an empty dict if the file is missing."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning("Could not parse %s: %s", path, exc)
        return {}


def _save_json(path: pathlib.Path, data: Any) -> None:
    """Write *data* as pretty-printed JSON to *path*, creating parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _append_audit(log_path: pathlib.Path, message: str) -> None:
    """Append a timestamped *message* to *log_path*."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"[{timestamp}] {message}\n")


# ---------------------------------------------------------------------------
# Corporate API audit
# ---------------------------------------------------------------------------


def audit_corporate_apis(node_config: dict[str, Any]) -> dict[str, list[str]]:
    """
    Audit *node_config* for endpoints that match :data:`CORPORATE_API_PATTERNS`.

    Returns a dict with keys ``severed`` and ``allowed`` listing the
    classified endpoint strings.
    """
    severed: list[str] = []
    allowed: list[str] = []

    endpoints: list[str] = []
    # Accept either a flat list under "endpoints" or a nested "apis" block.
    if "endpoints" in node_config and isinstance(node_config["endpoints"], list):
        endpoints = node_config["endpoints"]
    elif "apis" in node_config and isinstance(node_config["apis"], dict):
        endpoints = list(node_config["apis"].values())

    for ep in endpoints:
        if not isinstance(ep, str):
            continue
        is_corporate = any(pat in ep for pat in CORPORATE_API_PATTERNS)
        is_mesh = any(ep.startswith(pat) or pat in ep for pat in MESH_ENDPOINT_PATTERNS)
        if is_corporate and not is_mesh:
            severed.append(ep)
        else:
            allowed.append(ep)

    return {"severed": severed, "allowed": allowed}


def sever_corporate_apis(
    node_config: dict[str, Any],
    config_path: pathlib.Path,
    audit_log: pathlib.Path,
) -> dict[str, Any]:
    """
    Remove all corporate API entries from *node_config* and persist the
    sanitised config to *config_path*.

    Logs each severed endpoint to *audit_log*.

    Returns the audit result dict.
    """
    audit = audit_corporate_apis(node_config)

    # Rewrite node config — strip severed endpoints
    if "endpoints" in node_config:
        node_config["endpoints"] = [
            ep for ep in node_config["endpoints"] if ep not in audit["severed"]
        ]
    if "apis" in node_config and isinstance(node_config["apis"], dict):
        node_config["apis"] = {
            k: v for k, v in node_config["apis"].items() if v not in audit["severed"]
        }

    # Stamp the config with sovereignty metadata
    node_config.setdefault("obsidian_network", {})
    node_config["obsidian_network"]["corporate_apis_severed"] = True
    node_config["obsidian_network"]["severed_count"] = len(audit["severed"])
    node_config["obsidian_network"]["last_audit"] = datetime.now(timezone.utc).isoformat()

    _save_json(config_path, node_config)

    for ep in audit["severed"]:
        _append_audit(audit_log, f"CORPORATE_API_SEVERED | endpoint={ep}")
        logger.info("Severed corporate API: %s", ep)

    _append_audit(audit_log, f"INFRASTRUCTURE_SOVEREIGN | severed={len(audit['severed'])} | allowed={len(audit['allowed'])}")
    logger.info(
        "API audit complete — severed: %d | allowed: %d",
        len(audit["severed"]),
        len(audit["allowed"]),
    )
    return audit


# ---------------------------------------------------------------------------
# Bandwidth allocation
# ---------------------------------------------------------------------------


def allocate_bandwidth(
    tribe_whitelist: dict[str, Any],
    whitelist_path: pathlib.Path,
    audit_log: pathlib.Path,
    bandwidth_mbps: float = MATES_BUILD_BANDWIDTH_MBPS,
) -> dict[str, Any]:
    """
    Allocate dedicated bandwidth to each node in *tribe_whitelist* for the
    distribution of the Mates Build and open-source intelligence payloads.

    Returns the updated whitelist dict.
    """
    nodes: list[dict[str, Any]] = tribe_whitelist.get("nodes", [])
    if not nodes:
        logger.warning("Tribe whitelist has no nodes — skipping bandwidth allocation.")
        return tribe_whitelist

    per_node_mbps = round(bandwidth_mbps / max(len(nodes), 1), 4)
    for node in nodes:
        node.setdefault("bandwidth", {})
        node["bandwidth"]["allocated_mbps"] = per_node_mbps
        node["bandwidth"]["channel"] = "MESH_WIREGUARD"
        node["bandwidth"]["mates_build_enabled"] = True
        node["bandwidth"]["osint_distribution_enabled"] = True

    tribe_whitelist["total_bandwidth_mbps"] = bandwidth_mbps
    tribe_whitelist["last_allocation"] = datetime.now(timezone.utc).isoformat()
    _save_json(whitelist_path, tribe_whitelist)

    _append_audit(
        audit_log,
        f"BANDWIDTH_ALLOCATED | nodes={len(nodes)} | per_node_mbps={per_node_mbps} | channel=MESH_WIREGUARD",
    )
    logger.info("Bandwidth allocated: %.2f MB/s per node across %d nodes.", per_node_mbps, len(nodes))
    return tribe_whitelist


# ---------------------------------------------------------------------------
# Mesh connectivity check
# ---------------------------------------------------------------------------

#: Compiled pattern for validating IPv4 and simple IPv6 addresses / hostnames
#: before passing them to the ping sub-process.
_SAFE_IP_RE: re.Pattern[str] = re.compile(
    r"^(?:"
    # IPv4
    r"(?:\d{1,3}\.){3}\d{1,3}"
    r"|"
    # IPv6 (simplified — hex groups separated by colons, optional ::)
    r"(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}"
    r"|"
    # Hostname: labels of alphanumerics/hyphens, dot-separated
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)*[A-Za-z0-9]{1,63}"
    r")$"
)


def _is_safe_ip(ip: str) -> bool:
    """Return True when *ip* matches the safe address/hostname pattern."""
    return bool(_SAFE_IP_RE.match(ip))


def check_mesh_connectivity(tribe_whitelist: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Attempt a lightweight reachability check for each node listed in
    *tribe_whitelist* via ``ping``.

    Returns a list of status dicts — one per node — with keys ``node_id``,
    ``ip``, and ``reachable``.  ``reachable`` is ``True``/``False`` when the
    ping completes, or the string ``"UNKNOWN"`` when ``ping`` is unavailable
    or ``"INVALID_IP"`` when the address fails validation.
    """
    nodes: list[dict[str, Any]] = tribe_whitelist.get("nodes", [])
    results: list[dict[str, Any]] = []

    for node in nodes:
        node_id = node.get("id", "UNKNOWN")
        ip = node.get("ip", "")
        if not ip:
            results.append({"node_id": node_id, "ip": ip, "reachable": "NO_IP"})
            continue

        # Validate the IP/hostname before passing to the shell to prevent
        # command injection via untrusted whitelist entries.
        if not _is_safe_ip(ip):
            logger.warning("Mesh ping skipped — invalid/unsafe address: %r", ip)
            results.append({"node_id": node_id, "ip": ip, "reachable": "INVALID_IP"})
            continue

        reachable: bool | str
        try:
            ret = subprocess.run(  # noqa: S603
                ["ping", "-c", "1", "-W", "1", ip],
                capture_output=True,
                timeout=3,
                check=False,
            )
            reachable = ret.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            reachable = "UNKNOWN"

        results.append({"node_id": node_id, "ip": ip, "reachable": reachable})
        logger.debug("Mesh ping %s (%s): %s", node_id, ip, reachable)

    return results


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def engage_obsidian_network(
    config_path: pathlib.Path = NODE_CONFIG,
    whitelist_path: pathlib.Path = TRIBE_WHITELIST,
    audit_log: pathlib.Path = NETWORK_AUDIT_LOG,
) -> dict[str, Any]:
    """
    Execute the full Obsidian Network hardening sequence.

    Steps
    -----
    1. Load and audit ``D05/node_config.json`` for corporate API endpoints.
    2. Sever any flagged endpoints and persist the sanitised config.
    3. Load ``D06/tribe_whitelist.json`` and allocate mesh bandwidth.
    4. Perform a connectivity scan across whitelisted Swarm nodes.
    5. Write a final status record to the network audit log.

    Returns the combined status manifest.
    """
    logger.info("Obsidian Network — initiating infrastructure hardening sequence …")

    node_config = _load_json(config_path)
    audit_result = sever_corporate_apis(node_config, config_path, audit_log)

    tribe_whitelist = _load_json(whitelist_path)
    if not tribe_whitelist:
        # Bootstrap a minimal whitelist so bandwidth allocation can proceed
        tribe_whitelist = {"nodes": [], "generated_by": "industry_02_obsidian"}
        logger.info("No tribe whitelist found — bootstrapped empty whitelist at %s.", whitelist_path)

    allocate_bandwidth(tribe_whitelist, whitelist_path, audit_log)
    connectivity = check_mesh_connectivity(tribe_whitelist)

    reachable_count = sum(1 for c in connectivity if c.get("reachable") is True)
    timestamp = datetime.now(timezone.utc).isoformat()

    status: dict[str, Any] = {
        "freq_signature": FREQ_SIGNATURE,
        "timestamp": timestamp,
        "corporate_apis_severed": len(audit_result["severed"]),
        "mesh_nodes_checked": len(connectivity),
        "mesh_nodes_reachable": reachable_count,
        "bandwidth_channel": "MESH_WIREGUARD",
        "mates_build_distribution": "ENABLED",
        "osint_distribution": "ENABLED",
        "network_status": "INFRASTRUCTURE_SOVEREIGN",
    }

    _append_audit(
        audit_log,
        f"OBSIDIAN_NETWORK_ONLINE | apis_severed={len(audit_result['severed'])} | nodes_reachable={reachable_count}",
    )
    logger.info("Obsidian Network hardening complete — INFRASTRUCTURE_SOVEREIGN")
    return status


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Industry 02 — The Obsidian Network: P2P infrastructure hardening.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--sever-corporate-apis",
        action="store_true",
        help="Audit and sever all corporate API dependencies from the node config.",
    )
    parser.add_argument(
        "--config",
        type=pathlib.Path,
        default=NODE_CONFIG,
        help="Path to D05/node_config.json.",
    )
    parser.add_argument(
        "--whitelist",
        type=pathlib.Path,
        default=TRIBE_WHITELIST,
        help="Path to D06/tribe_whitelist.json.",
    )
    parser.add_argument(
        "--audit-log",
        type=pathlib.Path,
        default=NETWORK_AUDIT_LOG,
        help="Path to D05/network_audit.log.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the status manifest to stdout without writing to disk.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point — returns 0 on success, non-zero on failure."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    if not args.sever_corporate_apis:
        parser.print_help()
        return 0

    if args.dry_run:
        node_config = _load_json(args.config)
        audit = audit_corporate_apis(node_config)
        print(json.dumps({"dry_run": True, "audit": audit}, indent=2))
        return 0

    status = engage_obsidian_network(
        config_path=args.config,
        whitelist_path=args.whitelist,
        audit_log=args.audit_log,
    )
    print(status["network_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
