#!/usr/bin/env python3
"""
🌉 ASSET REMEDIATION BRIDGE — Legal-to-Financial Integration (v22.2124)

Wires two cross-module connections:

1. PvC Ledger → Asset Vault
   When a PvC dispute is resolved as "won", the recovered AUD amount is
   allocated to the XRP liquidity pool as Sovereign Interest.

2. Ute Wiring Log → Hardware Fleet Stability
   When the Ute's cross-feed short-circuit repair is marked complete, a
   9,293 Stability verification is triggered across the entire hardware fleet.

Usage:
    from bridge.asset_remediation import AssetRemediation

    bridge = AssetRemediation()
    bridge.apply_recovery("F001")       # route won fine to XRP pool
    bridge.check_ute_repair_status()    # trigger fleet check if repair done
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from legal.pvc_ledger import PvCLedger, DisputeOutcome
from inventory.asset_vault import AssetVault
from inventory.hardware_nodes import HardwareInventory

# Stability constant referenced in the convergence spec.
STABILITY_TARGET = 9_293


class AssetRemediation:
    """Bridge integrating the PvC Ledger, Asset Vault, and Hardware Inventory.

    Responsibilities
    ----------------
    * Route recovered fine amounts into the XRP liquidity pool.
    * Monitor the Ute repair log and trigger fleet stability checks on completion.
    """

    def __init__(
        self,
        *,
        ledger: Optional[PvCLedger] = None,
        vault: Optional[AssetVault] = None,
        hardware: Optional[HardwareInventory] = None,
        output_dir: Optional[Path] = None,
    ):
        self._ledger = ledger or PvCLedger()
        self._vault = vault or AssetVault()
        self._hardware = hardware or HardwareInventory()
        self.output_dir = output_dir or (Path(__file__).parent.parent / "data" / "asset_remediation")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._recovery_log: List[Dict[str, Any]] = []
        self._stability_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Accessors (allow callers to share module instances)
    # ------------------------------------------------------------------

    @property
    def ledger(self) -> PvCLedger:
        return self._ledger

    @property
    def vault(self) -> AssetVault:
        return self._vault

    @property
    def hardware(self) -> HardwareInventory:
        return self._hardware

    # ------------------------------------------------------------------
    # PvC Ledger → Asset Vault bridge
    # ------------------------------------------------------------------

    def apply_recovery(self, fine_id: str) -> Dict[str, Any]:
        """Route a resolved-won fine into the XRP liquidity pool.

        Parameters
        ----------
        fine_id: Fine ID that must already be registered and won in the ledger.

        Returns a remediation record describing the transfer.
        Raises ``ValueError`` when the dispute has not been won.
        """
        dispute = self._ledger.get_dispute(fine_id)
        if dispute["outcome"] != DisputeOutcome.WON:
            raise ValueError(
                f"Dispute '{fine_id}' has outcome '{dispute['outcome']}'; "
                "only 'won' disputes may be recovered."
            )

        recovered = dispute["recovered_aud"]

        # Record the recovered amount as an unclaimed/sovereign asset in the vault.
        vault_entry = self._vault.add_unclaimed_asset(
            description=f"Sovereign Interest — PvC Recovery [{fine_id}]: {dispute['description']}",
            source="PvC Ledger Recovery",
            value_aud=recovered,
        )

        record: Dict[str, Any] = {
            "fine_id": fine_id,
            "recovered_aud": recovered,
            "routed_to": "XRP Liquidity Pool (Sovereign Interest)",
            "vault_entry": vault_entry,
            "applied_at": datetime.now(timezone.utc).isoformat(),
        }
        self._recovery_log.append(record)
        return record

    def apply_all_recoveries(self) -> List[Dict[str, Any]]:
        """Apply ``apply_recovery`` for every unprocessed won dispute."""
        processed_ids = {r["fine_id"] for r in self._recovery_log}
        results = []
        for dispute in self._ledger.won_disputes():
            fid = dispute["fine_id"]
            if fid not in processed_ids:
                results.append(self.apply_recovery(fid))
        return results

    # ------------------------------------------------------------------
    # Ute Wiring Log → Fleet Stability bridge
    # ------------------------------------------------------------------

    def check_ute_repair_status(self) -> Dict[str, Any]:
        """Inspect the Ute's wiring diagnostics and trigger a fleet stability check.

        If the cross-feed short-circuit diagnostic has status ``"repaired"``,
        a full ``frequency_check_all()`` is run and a 9,293 Stability
        score is computed.

        Returns a dict with ``repair_complete`` and (when True)
        the full stability report.
        """
        node = self._hardware.get_node("node_03_ute")
        diag = node.get("diagnostics", {}).get("cross_feed_short_circuit", {})
        repair_complete = diag.get("status") == "repaired"

        result: Dict[str, Any] = {
            "node_id": "node_03_ute",
            "repair_complete": repair_complete,
            "diagnostic_status": diag.get("status", "unknown"),
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

        if repair_complete:
            stability = self.fleet_stability_check()
            result["stability_report"] = stability

        return result

    def fleet_stability_check(self) -> Dict[str, Any]:
        """Run a full 144Hz frequency check across all hardware nodes.

        Returns a stability report with a ``stability_score`` (out of
        ``STABILITY_TARGET = 9,293``) computed as the percentage of
        aligned nodes scaled to the target.
        """
        checks = self._hardware.frequency_check_all()
        total = len(checks)
        aligned = sum(1 for c in checks if c["aligned"])
        alignment_pct = aligned / total if total else 0.0
        stability_score = round(alignment_pct * STABILITY_TARGET)

        report: Dict[str, Any] = {
            "total_nodes": total,
            "aligned_nodes": aligned,
            "alignment_pct": round(alignment_pct * 100, 2),
            "stability_score": stability_score,
            "stability_target": STABILITY_TARGET,
            "stable": stability_score >= STABILITY_TARGET,
            "node_checks": checks,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
        self._stability_log.append(report)
        return report

    # ------------------------------------------------------------------
    # Persistence / status
    # ------------------------------------------------------------------

    def save(self, filename: str = "asset_remediation.json") -> Path:
        """Persist recovery and stability logs to disk."""
        payload = {
            "version": "v22.2124",
            "recovery_log": self._recovery_log,
            "stability_log": self._stability_log,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        out = self.output_dir / filename
        out.write_text(json.dumps(payload, indent=2))
        return out

    def status(self) -> Dict[str, Any]:
        """Return a summary of the remediation bridge state."""
        return {
            "recoveries_applied": len(self._recovery_log),
            "stability_checks_run": len(self._stability_log),
            "total_recovered_aud": self._ledger.total_recovered_aud(),
            "stability_target": STABILITY_TARGET,
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    bridge = AssetRemediation()

    bridge.ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera — Bruce Hwy")
    bridge.ledger.resolve_dispute("F001", outcome="won")
    recovery = bridge.apply_recovery("F001")

    print("🌉 ASSET REMEDIATION — Recovery")
    print(json.dumps({k: recovery[k] for k in ("fine_id", "recovered_aud", "routed_to")}, indent=2))

    stability = bridge.fleet_stability_check()
    print(f"\n🔊 Fleet Stability: {stability['stability_score']} / {stability['stability_target']}")
    print(json.dumps(bridge.status(), indent=2))


if __name__ == "__main__":
    main()
