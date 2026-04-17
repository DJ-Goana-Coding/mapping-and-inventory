#!/usr/bin/env python3
"""
💰 ASSET VAULT — Digital Asset Ledger (v22.2122)

Connects the Harvest Moon assets and BIND nodes:
  • XRP Ledger sync (milestone tracking)
  • Pi Network node integration
  • Queensland domain BIND node inventory
  • Unclaimed asset tracking (ASIC / Moneysmart)

Usage:
    from inventory.asset_vault import AssetVault

    vault = AssetVault()
    vault.xrp_ledger_sync(holdings_xrp=1500.0, price_aud=1.90)
    vault.pi_network_node(balance_pi=40.56)
    vault.domain_bind_node("mackaycrypto.com.au")
    print(vault.status())
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Default Queensland domains
# ---------------------------------------------------------------------------

DEFAULT_DOMAINS: List[Dict[str, str]] = [
    {"domain": "mackaycrypto.com.au", "registrar": "AU Registry", "status": "active"},
    {"domain": "qldai.au", "registrar": "AU Registry", "status": "active"},
]

TARGET_FREQUENCY_HZ = 144


class AssetVault:
    """Digital asset ledger and Queensland domain BIND node inventory.

    Tracks crypto holdings, Pi Network status, domain registrations,
    and unclaimed assets identified via ASIC / Moneysmart records.
    """

    def __init__(self, *, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (Path(__file__).parent.parent / "data" / "asset_vault")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._xrp_state: Optional[Dict[str, Any]] = None
        self._pi_state: Optional[Dict[str, Any]] = None
        self._domains: List[Dict[str, Any]] = [dict(d) for d in DEFAULT_DOMAINS]
        self._unclaimed_assets: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # XRP Ledger
    # ------------------------------------------------------------------

    def xrp_ledger_sync(self, *, holdings_xrp: float, price_aud: float) -> Dict[str, Any]:
        """Record XRP holdings and compute milestone status.

        Milestones tracked: AUD $1.90 price, $510 k portfolio target.
        """
        value_aud = round(holdings_xrp * price_aud, 2)

        self._xrp_state = {
            "asset": "XRP",
            "holdings": holdings_xrp,
            "price_aud": price_aud,
            "value_aud": value_aud,
            "milestones": {
                "price_1_90": price_aud >= 1.90,
                "portfolio_510k": value_aud >= 510_000,
            },
            "frequency_hz": TARGET_FREQUENCY_HZ,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._xrp_state

    # ------------------------------------------------------------------
    # Pi Network
    # ------------------------------------------------------------------

    def pi_network_node(self, *, balance_pi: float, rpc_status: str = "online") -> Dict[str, Any]:
        """Record Pi Network node balance and RPC server status."""
        self._pi_state = {
            "asset": "Pi Network",
            "balance_pi": balance_pi,
            "rpc_status": rpc_status,
            "frequency_hz": TARGET_FREQUENCY_HZ,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._pi_state

    # ------------------------------------------------------------------
    # Domain BIND nodes
    # ------------------------------------------------------------------

    def domain_bind_node(self, domain: str, *, registrar: str = "AU Registry",
                         status: str = "active") -> Dict[str, Any]:
        """Register a Queensland domain BIND node.

        If the domain already exists the record is updated; otherwise a new
        entry is appended.
        """
        for d in self._domains:
            if d["domain"] == domain:
                d["registrar"] = registrar
                d["status"] = status
                d["updated_at"] = datetime.now(timezone.utc).isoformat()
                return d

        entry: Dict[str, Any] = {
            "domain": domain,
            "registrar": registrar,
            "status": status,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._domains.append(entry)
        return entry

    def list_domains(self) -> List[Dict[str, Any]]:
        """Return all registered domain BIND nodes."""
        return list(self._domains)

    # ------------------------------------------------------------------
    # Unclaimed assets (ASIC / Moneysmart)
    # ------------------------------------------------------------------

    def add_unclaimed_asset(self, *, description: str, source: str = "ASIC Moneysmart",
                            abn: Optional[str] = None, value_aud: Optional[float] = None) -> Dict[str, Any]:
        """Register an unclaimed asset tied to a historical ABN."""
        entry: Dict[str, Any] = {
            "description": description,
            "source": source,
            "abn": abn,
            "estimated_value_aud": value_aud,
            "status": "identified",
            "identified_at": datetime.now(timezone.utc).isoformat(),
        }
        self._unclaimed_assets.append(entry)
        return entry

    def list_unclaimed_assets(self) -> List[Dict[str, Any]]:
        """Return all identified unclaimed assets."""
        return list(self._unclaimed_assets)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, filename: str = "asset_vault.json") -> Path:
        """Persist the full asset vault to disk."""
        payload = {
            "version": "v22.2122",
            "xrp": self._xrp_state,
            "pi_network": self._pi_state,
            "domains": self._domains,
            "unclaimed_assets": self._unclaimed_assets,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        out = self.output_dir / filename
        out.write_text(json.dumps(payload, indent=2))
        return out

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Return a summary of the digital asset vault."""
        return {
            "xrp_synced": self._xrp_state is not None,
            "pi_synced": self._pi_state is not None,
            "domains_registered": len(self._domains),
            "unclaimed_assets": len(self._unclaimed_assets),
            "target_frequency_hz": TARGET_FREQUENCY_HZ,
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    vault = AssetVault()

    vault.xrp_ledger_sync(holdings_xrp=1500.0, price_aud=1.90)
    vault.pi_network_node(balance_pi=40.56)

    print("💰 ASSET VAULT — Status")
    print(json.dumps(vault.status(), indent=2))

    print(f"\n🌐 Domains ({len(vault.list_domains())}):")
    for d in vault.list_domains():
        print(f"   • {d['domain']} [{d['status']}]")

    print(f"\n💎 XRP: {vault._xrp_state['value_aud']} AUD")
    print(f"🥧 Pi: {vault._pi_state['balance_pi']} Pi")


if __name__ == "__main__":
    main()
