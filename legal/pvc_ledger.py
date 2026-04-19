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
        }


# ═══════════════════════════════════════════════════════════════════════════
# CITIZEN VS. CORRUPTION (PvC) LEDGER — The Sovereign Audit (v22.2121)
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Forensic accountability ledger for trading & legal documentation
# Authority: Admiral Chance M.S. — OMNI-TIA Vascular Expansion
#
# Functions:
#   - generate_dossier():   Synthesise Washed Harvest data into reports
#   - track_demerits():     Log unjust levies (fines/demerit points)
#   - remediation_bot():    Auto-draft challenge letters (Sydney/QLD grid)
#
# Integration:
#   - Receives trade data from trading/harvest_moon.py
#   - Cross-references src/pvc_trigger_map.json
#   - Outputs to data/legal/dossiers/ and data/legal/challenges/
# ═══════════════════════════════════════════════════════════════════════════

import logging
from dataclasses import dataclass, field, asdict
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS — Relative Paths Only (Stainless Pipeline Rule #1)
# ═══════════════════════════════════════════════════════════════════════════

DOSSIER_DIR = Path("./data/legal/dossiers")
CHALLENGE_DIR = Path("./data/legal/challenges")
DEMERIT_DIR = Path("./data/legal/demerits")
PVC_TRIGGER_MAP = Path("./src/pvc_trigger_map.json")

logger = logging.getLogger("pvc_ledger")


class DossierType(Enum):
    """Types of dossier reports."""
    TRADE_AUDIT = "TRADE_AUDIT"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"
    CORRUPTION_SCAN = "CORRUPTION_SCAN"
    WASHED_HARVEST = "WASHED_HARVEST"


class DemeritCategory(Enum):
    """Categories of unjust levies."""
    TRAFFIC_FINE = "TRAFFIC_FINE"
    DEMERIT_POINTS = "DEMERIT_POINTS"
    PARKING_INFRINGEMENT = "PARKING_INFRINGEMENT"
    TOLL_LEVY = "TOLL_LEVY"
    COUNCIL_LEVY = "COUNCIL_LEVY"
    OTHER = "OTHER"


class ChallengeStatus(Enum):
    """Status of a challenge letter."""
    DRAFTED = "DRAFTED"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    UPHELD = "UPHELD"
    OVERTURNED = "OVERTURNED"


@dataclass
class DossierEntry:
    """A structured dossier entry for legal documentation."""
    dossier_id: str
    dossier_type: str
    title: str
    summary: str
    findings: list
    evidence_refs: list
    risk_level: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict = field(default_factory=dict)


@dataclass
class DemeritRecord:
    """Record of an unjust levy for tracking and challenge."""
    record_id: str
    category: str
    description: str
    amount: float
    date_issued: str
    issuing_authority: str
    location: str
    infringement_number: str = ""
    demerit_points: int = 0
    challenge_status: str = ChallengeStatus.DRAFTED.value
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    evidence: list = field(default_factory=list)


@dataclass
class ChallengeLetter:
    """Auto-generated challenge letter."""
    challenge_id: str
    demerit_record_id: str
    recipient: str
    subject: str
    body: str
    legal_basis: list
    status: str = ChallengeStatus.DRAFTED.value
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ═══════════════════════════════════════════════════════════════════════════
# SOVEREIGN RIGHTS DATABASE — Sydney / Queensland Grid
# ═══════════════════════════════════════════════════════════════════════════

SOVEREIGN_RIGHTS_DB = {
    "nsw_traffic": {
        "jurisdiction": "New South Wales",
        "challenge_grounds": [
            "Defective signage (AS 1742 compliance)",
            "Calibration certificate expired or unavailable",
            "Operator certification lapsed",
            "Chain-of-custody break in evidence",
            "Statutory declaration irregularities",
            "Notice period non-compliance (21-day rule)",
        ],
        "relevant_acts": [
            "Road Transport Act 2013 (NSW)",
            "Fines Act 1996 (NSW)",
            "Road Rules 2014 (NSW)",
        ],
        "appeal_bodies": [
            "Revenue NSW — Internal Review",
            "Local Court of NSW",
            "NSW Civil and Administrative Tribunal (NCAT)",
        ],
    },
    "qld_traffic": {
        "jurisdiction": "Queensland",
        "challenge_grounds": [
            "Speed camera signage deficiency",
            "Calibration non-compliance",
            "Incorrect speed zone gazettal",
            "Officer identification failure",
            "Procedural irregularity in infringement issue",
            "Ungazetted road section",
        ],
        "relevant_acts": [
            "Transport Operations (Road Use Management) Act 1995 (QLD)",
            "State Penalties Enforcement Act 1999 (QLD)",
            "Traffic Regulation 1962 (QLD)",
        ],
        "appeal_bodies": [
            "Queensland Revenue Office — Internal Review",
            "Magistrates Court of Queensland",
            "Queensland Civil and Administrative Tribunal (QCAT)",
        ],
    },
    "general_sovereign": {
        "jurisdiction": "Federal / Constitutional",
        "challenge_grounds": [
            "Constitutional validity of the levy",
            "Procedural fairness denial",
            "Natural justice breach",
            "Unreasonable administrative action",
            "Section 75(v) — High Court judicial review",
        ],
        "relevant_acts": [
            "Commonwealth of Australia Constitution Act 1901",
            "Administrative Decisions (Judicial Review) Act 1977",
            "Human Rights Act 2019 (QLD)",
        ],
        "appeal_bodies": [
            "Federal Court of Australia",
            "High Court of Australia",
            "Administrative Appeals Tribunal",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# FUNCTION 1: generate_dossier — Synthesise Reports
# ═══════════════════════════════════════════════════════════════════════════

class DossierGenerator:
    """Synthesises Washed Harvest data into formal, structured reports."""

    def __init__(self):
        DOSSIER_DIR.mkdir(parents=True, exist_ok=True)
        self.trigger_map = self._load_trigger_map()
        self._counter = 0

    def _load_trigger_map(self) -> dict:
        """Load the PvC Trigger Map for cross-referencing."""
        if PVC_TRIGGER_MAP.exists():
            return json.loads(PVC_TRIGGER_MAP.read_text())
        logger.warning("PvC trigger map not found at %s", PVC_TRIGGER_MAP)
        return {}

    def generate_dossier(
        self,
        research_data: dict,
        dossier_type: DossierType = DossierType.WASHED_HARVEST,
    ) -> DossierEntry:
        """
        Synthesise research data into a formal, structured dossier.

        Parameters
        ----------
        research_data : dict
            Raw data from the Washed Harvest or trading modules.
        dossier_type : DossierType
            Classification of the dossier.
        """
        self._counter += 1
        dossier_id = (
            f"PVC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            f"-{self._counter:04d}"
        )

        # Extract findings from research data
        findings = self._extract_findings(research_data)

        # Cross-reference with trigger map
        evidence_refs = self._cross_reference_triggers(research_data)

        # Assess risk level
        risk_level = self._assess_risk(findings)

        dossier = DossierEntry(
            dossier_id=dossier_id,
            dossier_type=dossier_type.value,
            title=research_data.get("title", "Untitled Dossier"),
            summary=research_data.get("summary", ""),
            findings=findings,
            evidence_refs=evidence_refs,
            risk_level=risk_level,
            metadata={
                "source": research_data.get("source", "unknown"),
                "total_findings": len(findings),
                "trigger_matches": len(evidence_refs),
            },
        )

        # Persist dossier
        self._persist_dossier(dossier)
        logger.info("[DOSSIER] Generated %s — %d findings, risk: %s",
                     dossier_id, len(findings), risk_level)
        return dossier

    def _extract_findings(self, data: dict) -> list:
        """Extract actionable findings from research data."""
        findings = []
        if "trades" in data:
            for trade in data["trades"]:
                findings.append({
                    "type": "trade_record",
                    "description": (
                        f"{trade.get('action', 'UNKNOWN')} "
                        f"@ ${trade.get('price', 0):.4f}"
                    ),
                    "timestamp": trade.get("timestamp", ""),
                })
        if "violations" in data:
            for violation in data["violations"]:
                findings.append({
                    "type": "compliance_violation",
                    "description": violation.get("description", ""),
                    "severity": violation.get("severity", "MEDIUM"),
                    "code": violation.get("code", ""),
                })
        if "anomalies" in data:
            for anomaly in data["anomalies"]:
                findings.append({
                    "type": "anomaly",
                    "description": str(anomaly),
                })
        return findings

    def _cross_reference_triggers(self, data: dict) -> list:
        """Cross-reference data against the PvC Trigger Map."""
        refs = []
        if not self.trigger_map:
            return refs
        legislative = self.trigger_map.get("legislative_codes", {})
        data_str = json.dumps(data).lower()
        for code_key, code_info in legislative.items():
            for flag in code_info.get("audit_flags", []):
                if flag.lower() in data_str:
                    refs.append({
                        "trigger_code": code_info.get("code", code_key),
                        "trigger_name": code_info.get("name", ""),
                        "matched_flag": flag,
                        "severity": code_info.get("severity", "MEDIUM"),
                    })
        return refs

    def _assess_risk(self, findings: list) -> str:
        """Assess overall risk level from findings."""
        if not findings:
            return "LOW"
        severity_scores = {
            "CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1,
        }
        max_severity = 0
        for f in findings:
            sev = f.get("severity", "LOW")
            max_severity = max(max_severity, severity_scores.get(sev, 1))
        if max_severity >= 4:
            return "CRITICAL"
        if max_severity >= 3:
            return "HIGH"
        if max_severity >= 2:
            return "MEDIUM"
        return "LOW"

    def _persist_dossier(self, dossier: DossierEntry) -> None:
        """Persist dossier to disk."""
        out_file = DOSSIER_DIR / f"{dossier.dossier_id}.json"
        out_file.write_text(json.dumps(asdict(dossier), indent=2))


# ═══════════════════════════════════════════════════════════════════════════
# FUNCTION 2: track_demerits — Log Unjust Levies
# ═══════════════════════════════════════════════════════════════════════════

class DemeritTracker:
    """Tracks unjust levies (traffic fines, demerit points) for challenge."""

    def __init__(self):
        DEMERIT_DIR.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def track_demerits(
        self,
        category: DemeritCategory,
        description: str,
        amount: float,
        date_issued: str,
        issuing_authority: str,
        location: str,
        infringement_number: str = "",
        demerit_points: int = 0,
        evidence: Optional[list] = None,
    ) -> DemeritRecord:
        """
        Log an unjust levy for tracking and automated challenge.

        Parameters
        ----------
        category : DemeritCategory
            Type of infringement (TRAFFIC_FINE, DEMERIT_POINTS, etc.).
        description : str
            Human-readable description of the levy.
        amount : float
            Dollar amount of the fine.
        date_issued : str
            Date the infringement was issued (ISO format).
        issuing_authority : str
            Authority that issued the levy.
        location : str
            Location where the infringement occurred.
        infringement_number : str
            Official infringement reference number.
        demerit_points : int
            Number of demerit points attached.
        evidence : list, optional
            Supporting evidence file paths.
        """
        self._counter += 1
        record_id = (
            f"DEM-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            f"-{self._counter:04d}"
        )

        record = DemeritRecord(
            record_id=record_id,
            category=category.value,
            description=description,
            amount=amount,
            date_issued=date_issued,
            issuing_authority=issuing_authority,
            location=location,
            infringement_number=infringement_number,
            demerit_points=demerit_points,
            evidence=evidence or [],
        )

        self._persist_record(record)
        logger.info(
            "[DEMERIT] Tracked %s — $%.2f, %d points, %s",
            record_id, amount, demerit_points, category.value,
        )
        return record

    def list_records(self) -> list[DemeritRecord]:
        """List all tracked demerit records."""
        records = []
        for f in sorted(DEMERIT_DIR.glob("DEM-*.json")):
            data = json.loads(f.read_text())
            records.append(DemeritRecord(**data))
        return records

    def total_levies(self) -> dict:
        """Calculate total levies tracked."""
        records = self.list_records()
        return {
            "total_records": len(records),
            "total_amount": sum(r.amount for r in records),
            "total_demerit_points": sum(r.demerit_points for r in records),
            "by_category": self._group_by_category(records),
        }

    def _group_by_category(self, records: list[DemeritRecord]) -> dict:
        """Group records by category."""
        groups: dict[str, dict] = {}
        for r in records:
            if r.category not in groups:
                groups[r.category] = {"count": 0, "total_amount": 0.0}
            groups[r.category]["count"] += 1
            groups[r.category]["total_amount"] += r.amount
        return groups

    def _persist_record(self, record: DemeritRecord) -> None:
        """Persist demerit record to disk."""
        out_file = DEMERIT_DIR / f"{record.record_id}.json"
        out_file.write_text(json.dumps(asdict(record), indent=2))


# ═══════════════════════════════════════════════════════════════════════════
# FUNCTION 3: remediation_bot — Auto-Draft Challenge Letters
# ═══════════════════════════════════════════════════════════════════════════

class RemediationBot:
    """
    Automatically drafts challenge letters using the Sovereign Rights
    database for the Sydney/Queensland grid.
    """

    def __init__(self):
        CHALLENGE_DIR.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def remediation_bot(self, record: DemeritRecord) -> ChallengeLetter:
        """
        Auto-draft a challenge letter for a demerit record.

        Selects the appropriate Sovereign Rights database entry
        based on the jurisdiction inferred from the location.
        """
        jurisdiction = self._infer_jurisdiction(record.location)
        rights_db = SOVEREIGN_RIGHTS_DB.get(jurisdiction, SOVEREIGN_RIGHTS_DB["general_sovereign"])

        self._counter += 1
        challenge_id = (
            f"CHL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            f"-{self._counter:04d}"
        )

        # Select applicable challenge grounds
        legal_basis = self._select_grounds(record, rights_db)

        # Draft the letter
        body = self._draft_letter(record, rights_db, legal_basis)

        # Determine recipient
        recipient = self._get_recipient(rights_db)

        letter = ChallengeLetter(
            challenge_id=challenge_id,
            demerit_record_id=record.record_id,
            recipient=recipient,
            subject=(
                f"Internal Review Request — Infringement "
                f"{record.infringement_number or record.record_id}"
            ),
            body=body,
            legal_basis=legal_basis,
        )

        self._persist_challenge(letter)
        logger.info("[REMEDIATION] Challenge %s drafted for %s — %s",
                     challenge_id, record.record_id, jurisdiction)
        return letter

    def _infer_jurisdiction(self, location: str) -> str:
        """Infer jurisdiction from location string."""
        loc_lower = location.lower()
        nsw_markers = ["sydney", "nsw", "new south wales", "parramatta",
                        "wollongong", "newcastle"]
        qld_markers = ["queensland", "qld", "brisbane", "gold coast",
                        "sunshine coast", "cairns", "townsville"]
        for marker in nsw_markers:
            if marker in loc_lower:
                return "nsw_traffic"
        for marker in qld_markers:
            if marker in loc_lower:
                return "qld_traffic"
        return "general_sovereign"

    def _select_grounds(self, record: DemeritRecord, rights_db: dict) -> list:
        """Select applicable challenge grounds."""
        # Use all available grounds for the jurisdiction
        grounds = rights_db.get("challenge_grounds", [])
        # Include relevant acts as supporting legislation
        return [
            {"ground": g, "acts": rights_db.get("relevant_acts", [])}
            for g in grounds[:3]  # Top 3 most applicable
        ]

    def _get_recipient(self, rights_db: dict) -> str:
        """Get the first appeal body as recipient."""
        bodies = rights_db.get("appeal_bodies", [])
        return bodies[0] if bodies else "Issuing Authority — Internal Review"

    def _draft_letter(
        self,
        record: DemeritRecord,
        rights_db: dict,
        legal_basis: list,
    ) -> str:
        """Draft the formal challenge letter."""
        jurisdiction = rights_db.get("jurisdiction", "General")
        acts = rights_db.get("relevant_acts", [])
        date_str = datetime.now(timezone.utc).strftime("%d %B %Y")

        lines = [
            f"Date: {date_str}",
            "",
            f"Re: Request for Internal Review",
            f"Infringement Number: {record.infringement_number or 'N/A'}",
            f"Date of Infringement: {record.date_issued}",
            f"Amount: ${record.amount:.2f}",
            f"Location: {record.location}",
            "",
            "To Whom It May Concern,",
            "",
            f"I write to request an internal review of the above "
            f"infringement notice issued under the {jurisdiction} "
            f"jurisdiction.",
            "",
            f"DESCRIPTION OF INFRINGEMENT:",
            f"{record.description}",
            "",
            "GROUNDS FOR REVIEW:",
            "",
        ]

        for i, basis in enumerate(legal_basis, 1):
            lines.append(f"{i}. {basis['ground']}")
            if basis.get("acts"):
                lines.append(f"   Relevant legislation: {', '.join(basis['acts'][:2])}")
            lines.append("")

        lines.extend([
            "SUPPORTING EVIDENCE:",
            "",
        ])

        if record.evidence:
            for ev in record.evidence:
                lines.append(f"  - {ev}")
        else:
            lines.append("  (Evidence to be attached)")

        lines.extend([
            "",
            "RELIEF SOUGHT:",
            f"  - Withdrawal of infringement notice",
            f"  - Refund of ${record.amount:.2f}" if record.amount > 0 else "",
            f"  - Removal of {record.demerit_points} demerit point(s)" if record.demerit_points > 0 else "",
            "",
            "I respectfully request that this matter be reviewed in "
            "accordance with principles of natural justice and "
            "procedural fairness.",
            "",
            "Yours faithfully,",
            "[Name]",
            "[Address]",
            "[Contact]",
        ])

        return "\n".join(line for line in lines if line is not None)

    def _persist_challenge(self, letter: ChallengeLetter) -> None:
        """Persist challenge letter to disk."""
        out_file = CHALLENGE_DIR / f"{letter.challenge_id}.json"
        out_file.write_text(json.dumps(asdict(letter), indent=2))

        # Also save a human-readable text version
        txt_file = CHALLENGE_DIR / f"{letter.challenge_id}.txt"
        txt_file.write_text(letter.body)


# ═══════════════════════════════════════════════════════════════════════════
# UNIFIED PVC LEDGER — Convenience Interface
# ═══════════════════════════════════════════════════════════════════════════

class PvCSovereignLedger:
    """
    Unified Citizen vs. Corruption Sovereign Ledger interface.

    Combines dossier generation, demerit tracking, and automated
    remediation into a single API. Distinct from :class:`PvCLedger`
    (the Person-vs-Camera dispute tracker defined above).
    """

    def __init__(self):
        self.dossier_gen = DossierGenerator()
        self.demerit_tracker = DemeritTracker()
        self.remediation = RemediationBot()
        logger.info("[PvC LEDGER] System ONLINE — Sovereign Audit active")

    def generate_dossier(self, research_data: dict, **kwargs) -> DossierEntry:
        """Generate a dossier from research data."""
        return self.dossier_gen.generate_dossier(research_data, **kwargs)

    def track_demerits(self, **kwargs) -> DemeritRecord:
        """Track an unjust levy."""
        return self.demerit_tracker.track_demerits(**kwargs)

    def remediation_bot(self, record: DemeritRecord) -> ChallengeLetter:
        """Auto-draft a challenge letter."""
        return self.remediation.remediation_bot(record)

    def full_pipeline(
        self,
        category: DemeritCategory,
        description: str,
        amount: float,
        date_issued: str,
        issuing_authority: str,
        location: str,
        **kwargs,
    ) -> dict:
        """
        Full pipeline: track demerit → generate dossier → draft challenge.
        """
        # Step 1: Track the demerit
        record = self.track_demerits(
            category=category,
            description=description,
            amount=amount,
            date_issued=date_issued,
            issuing_authority=issuing_authority,
            location=location,
            **kwargs,
        )

        # Step 2: Generate dossier
        dossier = self.generate_dossier({
            "title": f"Demerit Challenge — {record.record_id}",
            "summary": description,
            "source": issuing_authority,
            "violations": [{
                "description": description,
                "severity": "HIGH" if amount >= 500 else "MEDIUM",
                "code": record.infringement_number,
            }],
        })

        # Step 3: Draft challenge letter
        challenge = self.remediation_bot(record)

        return {
            "record": asdict(record),
            "dossier": asdict(dossier),
            "challenge": asdict(challenge),
            "pipeline_status": "COMPLETE",
        }

    def status(self) -> dict:
        """Return PvC Ledger system status."""
        totals = self.demerit_tracker.total_levies()
        return {
            "system": "PvC Ledger — Sovereign Audit",
            "version": "v22.2121",
            "total_demerits": totals["total_records"],
            "total_levies_amount": totals["total_amount"],
            "total_demerit_points": totals["total_demerit_points"],
            "by_category": totals["by_category"],
            "status": "ONLINE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

# ═══════════════════════════════════════════════════════════════════════════
# MAIN — Boot Sequence
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Boot the PvC Sovereign Ledger and run a diagnostic cycle."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("⚖️  PvC LEDGER — Sovereign Audit Ignition")
    print("=" * 60)

    ledger = PvCSovereignLedger()

    # Diagnostic: Track a sample demerit
    result = ledger.full_pipeline(
        category=DemeritCategory.TRAFFIC_FINE,
        description="Alleged speed camera infringement — camera signage "
                    "placement potentially non-compliant with AS 1742",
        amount=800.00,
        date_issued="2026-03-15",
        issuing_authority="Revenue NSW",
        location="Sydney, NSW",
        infringement_number="INF-2026-NSW-001234",
        demerit_points=4,
    )

    print(f"\n📋 Demerit Tracked: {result['record']['record_id']}")
    print(f"   Amount: ${result['record']['amount']:.2f}")
    print(f"   Points: {result['record']['demerit_points']}")
    print(f"\n📁 Dossier Generated: {result['dossier']['dossier_id']}")
    print(f"   Findings: {result['dossier']['metadata']['total_findings']}")
    print(f"   Risk: {result['dossier']['risk_level']}")
    print(f"\n📨 Challenge Drafted: {result['challenge']['challenge_id']}")
    print(f"   Recipient: {result['challenge']['recipient']}")
    print(f"   Status: {result['challenge']['status']}")

    # System status
    status = ledger.status()
    print(f"\n⚖️  System: {status['system']}")
    print(f"   Total Demerits: {status['total_demerits']}")
    print(f"   Total Levies: ${status['total_levies_amount']:.2f}")

    print("\n🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors")


if __name__ == "__main__":
    main()
