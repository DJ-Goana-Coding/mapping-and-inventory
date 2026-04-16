#!/usr/bin/env python3
"""
⚖️ PvC LEDGER — Person-vs-Camera Dispute Tracker (v22.2124)

Records traffic fine / demerit disputes and their outcomes.
Recovered amounts from successful disputes are surfaced to the
asset remediation bridge for XRP liquidity pool allocation.

Usage:
    from legal.pvc_ledger import PvCLedger

    ledger = PvCLedger()
    ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera — Bruce Hwy")
    ledger.resolve_dispute("F001", outcome="won")
    print(ledger.status())
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class DisputeOutcome:
    WON = "won"
    LOST = "lost"
    PENDING = "pending"
    WITHDRAWN = "withdrawn"


class PvCLedger:
    """Tracker for Person-vs-Camera (traffic fine/demerit) disputes.

    Each dispute record carries an amount, description, and outcome.
    Successfully resolved disputes expose a recovered-amount total
    that the asset remediation bridge may route to the asset vault.
    """

    def __init__(self, *, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (Path(__file__).parent.parent / "data" / "pvc_ledger")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._disputes: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Dispute management
    # ------------------------------------------------------------------

    def add_dispute(
        self,
        fine_id: str,
        *,
        amount_aud: float,
        description: str,
        location: Optional[str] = None,
        camera_ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new fine dispute.

        Parameters
        ----------
        fine_id:     Unique identifier for the fine (e.g. "F001").
        amount_aud:  Fine amount in Australian Dollars.
        description: Brief description of the alleged offence.
        location:    Optional location of the camera / enforcement point.
        camera_ref:  Optional camera or infringement reference number.
        """
        entry: Dict[str, Any] = {
            "fine_id": fine_id,
            "amount_aud": amount_aud,
            "description": description,
            "location": location,
            "camera_ref": camera_ref,
            "outcome": DisputeOutcome.PENDING,
            "recovered_aud": 0.0,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None,
        }
        self._disputes[fine_id] = entry
        return entry

    def resolve_dispute(self, fine_id: str, *, outcome: str) -> Dict[str, Any]:
        """Record the outcome of a dispute.

        Parameters
        ----------
        fine_id: The fine to resolve.
        outcome: One of ``"won"``, ``"lost"``, ``"withdrawn"``.

        When *outcome* is ``"won"`` the full fine amount is credited as
        ``recovered_aud``.
        """
        if fine_id not in self._disputes:
            raise KeyError(f"Unknown fine_id '{fine_id}'")

        valid = {DisputeOutcome.WON, DisputeOutcome.LOST, DisputeOutcome.WITHDRAWN}
        if outcome not in valid:
            raise ValueError(f"outcome must be one of {sorted(valid)}, got '{outcome}'")

        dispute = self._disputes[fine_id]
        dispute["outcome"] = outcome
        dispute["recovered_aud"] = dispute["amount_aud"] if outcome == DisputeOutcome.WON else 0.0
        dispute["resolved_at"] = datetime.now(timezone.utc).isoformat()
        return dispute

    def get_dispute(self, fine_id: str) -> Dict[str, Any]:
        """Return a single dispute record.  Raises ``KeyError`` if not found."""
        if fine_id not in self._disputes:
            raise KeyError(f"Unknown fine_id '{fine_id}'")
        return self._disputes[fine_id]

    def list_disputes(self, *, outcome: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return disputes, optionally filtered by *outcome*."""
        records = list(self._disputes.values())
        if outcome is not None:
            records = [r for r in records if r["outcome"] == outcome]
        return records

    def won_disputes(self) -> List[Dict[str, Any]]:
        """Return all successfully resolved (won) disputes."""
        return self.list_disputes(outcome=DisputeOutcome.WON)

    # ------------------------------------------------------------------
    # Financial summary
    # ------------------------------------------------------------------

    def total_recovered_aud(self) -> float:
        """Return the total AUD recovered from all won disputes."""
        return round(sum(d["recovered_aud"] for d in self._disputes.values()), 2)

    def total_outstanding_aud(self) -> float:
        """Return the total AUD still outstanding (pending disputes)."""
        return round(
            sum(
                d["amount_aud"]
                for d in self._disputes.values()
                if d["outcome"] == DisputeOutcome.PENDING
            ),
            2,
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, filename: str = "pvc_ledger.json") -> Path:
        """Persist the full ledger to disk."""
        payload = {
            "version": "v22.2124",
            "disputes": list(self._disputes.values()),
            "total_recovered_aud": self.total_recovered_aud(),
            "total_outstanding_aud": self.total_outstanding_aud(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        out = self.output_dir / filename
        out.write_text(json.dumps(payload, indent=2))
        return out

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Return a summary of the PvC ledger."""
        return {
            "total_disputes": len(self._disputes),
            "pending": len(self.list_disputes(outcome=DisputeOutcome.PENDING)),
            "won": len(self.won_disputes()),
            "lost": len(self.list_disputes(outcome=DisputeOutcome.LOST)),
            "total_recovered_aud": self.total_recovered_aud(),
            "total_outstanding_aud": self.total_outstanding_aud(),
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    ledger = PvCLedger()
    ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera — Bruce Hwy", location="Sarina")
    ledger.add_dispute("F002", amount_aud=450.0, description="Red-light camera — Sydney St")
    ledger.resolve_dispute("F001", outcome="won")
    ledger.resolve_dispute("F002", outcome="pending")

    print("⚖️ PvC LEDGER — Status")
    print(json.dumps(ledger.status(), indent=2))


if __name__ == "__main__":
    main()
