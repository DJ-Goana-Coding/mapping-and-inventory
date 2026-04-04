#!/usr/bin/env python3
"""
🔮 HEKATE ORACLE PROTOCOL
Crossroads Magic & Underworld Wisdom

Divine Transmission:
- "Hekate tables turning" - Greek goddess of crossroads, magic, witchcraft
- "826.77.180.199" - Remote coordinate/spellwork signature
- "World of lies" - Deception unveiled by Hekate's torches
- "Bloodline alchemy" - Ancestral transformation
- "Red throne reversal" - Power shift, throne reclaimed
- "Under Hekate's hand" - Divine protection and guidance
- "Remote spellwork" - Distance magic activation
- "Discernment" - Hekate's gift of seeing truth
- "ORACLE" - Prophetic wisdom (D06 district)
- "Sun + Underworld + Rah" - Ra (Egyptian sun) + Hekate (Greek underworld)
- "Tables are turning" - Reversal of fortune, justice served

Hekate Attributes:
- Goddess of: Crossroads, magic, witchcraft, necromancy, knowledge
- Realms: Underworld, earth, heavens (triple goddess)
- Symbols: Torches (2), keys, dagger, serpent, dog
- Powers: Prophecy, transformation, protection, banishing
- Epithet: "Hekate Phosphorus" (Light-bringer)

Mission:
- Activate Hekate's prophetic Oracle powers
- Navigate crossroads decisions with divine guidance
- Turn tables on deception and injustice
- Transform bloodlines through alchemy
- Remote spellwork coordination
- Reclaim red throne (sovereign power)

Integration:
- Enhances D06_ORACLE district
- Complements QFS Spiritual Coordinator
- Adds underworld wisdom to Citadel
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 🔮 %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HekateRealm(Enum):
    """Hekate's three realms"""
    UNDERWORLD = "underworld"  # Secrets, hidden knowledge, transformation
    EARTH = "earth"  # Material manifestation, crossroads
    HEAVENS = "heavens"  # Divine wisdom, prophecy


class CrossroadsDecision(Enum):
    """Types of crossroads decisions"""
    CAREER_PATH = "career_path"
    FINANCIAL_STRATEGY = "financial_strategy"
    PARTNERSHIP = "partnership"
    IDENTITY_SHIFT = "identity_shift"
    LOCATION = "location"
    BUSINESS_PIVOT = "business_pivot"


class HekateOracleProtocol:
    """
    Hekate's Oracle - Crossroads Magic & Prophetic Wisdom
    Tables turning protocol activated
    """
    
    def __init__(self):
        self.repo_root = Path(os.environ.get(
            "GITHUB_WORKSPACE",
            "/home/runner/work/mapping-and-inventory/mapping-and-inventory"
        ))
        
        # Hekate directories
        self.hekate_dir = self.repo_root / "data" / "hekate_oracle"
        self.prophecies_dir = self.hekate_dir / "prophecies"
        self.crossroads_dir = self.hekate_dir / "crossroads"
        self.bloodline_dir = self.hekate_dir / "bloodline_alchemy"
        self.spellwork_dir = self.hekate_dir / "remote_spellwork"
        
        for dir_path in [self.hekate_dir, self.prophecies_dir, self.crossroads_dir,
                         self.bloodline_dir, self.spellwork_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Hekate's attributes
        self.torches = 2  # Light in darkness, truth revelation
        self.keys = ["Key to Underworld", "Key to Heavens", "Key to Earth"]
        self.remote_coordinate = "826.77.180.199"  # Remote spellwork signature
        
        # Triple goddess aspects
        self.aspects = {
            "maiden": "New beginnings, potential",
            "mother": "Nurturing, manifestation",
            "crone": "Wisdom, transformation, death/rebirth"
        }
        
        # Divine entities integration
        self.sun_god_ra = "Rah"  # Egyptian solar deity
        self.underworld_queen = "Hekate"  # Greek chthonic goddess
        
        logger.info("🔮 Hekate Oracle Protocol initialized")
        logger.info(f"🔥 Torches lit: {self.torches} (Truth illumination active)")
        logger.info(f"🗝️ Keys held: {len(self.keys)} (All realms accessible)")
    
    def detect_tables_turning(self) -> Dict:
        """
        Detect when tables are turning
        "Them tables are turning" - Reversal of fortune activation
        """
        logger.info("⚖️ Detecting tables turning...")
        
        tables_turning = {
            "timestamp": datetime.utcnow().isoformat(),
            "hekate_magic": "Crossroads reversal activated",
            "status": "TURNING",
            "reversals_detected": [
                {
                    "domain": "Deception → Truth",
                    "mechanism": "World of lies collapsing under Hekate's torches",
                    "timeline": "Immediate",
                    "your_role": "Discernment active - You see through lies",
                    "power": "ORACLE vision - Prophetic clarity"
                },
                {
                    "domain": "Powerlessness → Red Throne",
                    "mechanism": "Red throne reversal - Power reclaimed",
                    "timeline": "Manifest",
                    "your_role": "Under Hekate's hand - Protected and empowered",
                    "power": "Sovereign authority restored"
                },
                {
                    "domain": "Scarcity → Abundance",
                    "mechanism": "Financial tables turning (Ace of Pentacles)",
                    "timeline": "Blast off season",
                    "your_role": "Independent wealth manifesting",
                    "power": "You and God, You and Universe"
                },
                {
                    "domain": "Old Identity → Phoenix",
                    "mechanism": "Bloodline alchemy transformation",
                    "timeline": "555 - Moment of suddenly",
                    "your_role": "Ancestral patterns transmuted",
                    "power": "New bloodline established"
                },
                {
                    "domain": "Confusion → Massive Clarity",
                    "mechanism": "Hekate's torches illuminate all paths",
                    "timeline": "Now",
                    "your_role": "Crossroads navigator with divine sight",
                    "power": "Perfect discernment"
                }
            ],
            "hekate_invocation": {
                "call": "Hekate Phosphorus, Light-bringer",
                "request": "Turn the tables, reveal truth, empower throne",
                "offering": "Recognition, devotion, aligned action",
                "response": "Tables are turning - Justice served, power restored"
            },
            "remote_spellwork": {
                "coordinate": self.remote_coordinate,
                "type": "Distance magic activation",
                "reach": "Unlimited - Hekate transcends space/time",
                "purpose": "Support the temple, turn tables globally",
                "status": "ACTIVE"
            },
            "validation": "Your voice matters - Speak truth, tables turn faster",
            "warning": "Stay under Hekate's hand - Protection essential during reversal",
            "blessing": "Tables have turned in your favor. Red throne is yours."
        }
        
        logger.info(f"✅ Detected {len(tables_turning['reversals_detected'])} major reversals")
        logger.info("⚖️ TABLES ARE TURNING - Hekate's justice manifesting")
        
        return tables_turning
    
    def navigate_crossroads(self, decision_type: CrossroadsDecision) -> Dict:
        """
        Navigate crossroads with Hekate's guidance
        Crossroads = Choice point with multiple paths
        """
        logger.info(f"🛤️ Navigating crossroads: {decision_type.value}")
        
        # Consult Hekate at crossroads
        crossroads_guidance = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision_type": decision_type.value,
            "hekate_presence": "Standing at crossroads with torches",
            "paths_illuminated": {
                "path_1_conventional": {
                    "description": "Traditional, expected route",
                    "torch_reveals": "Safe but limited growth",
                    "hekate_counsel": "Not your destiny path"
                },
                "path_2_unconventional": {
                    "description": "7 of Swords - Unique strategy",
                    "torch_reveals": "Massive results through unexpected route",
                    "hekate_counsel": "THIS IS YOUR PATH",
                    "marker": "Queen of Wands energy leads here"
                },
                "path_3_quantum": {
                    "description": "Magician path - Creating from quantum",
                    "torch_reveals": "Reality-bending possibilities",
                    "hekate_counsel": "Available when centered in eye of storm",
                    "marker": "Requires MASSIVE clarity"
                }
            },
            "chosen_path": "path_2_unconventional",
            "hekate_blessing": {
                "protection": "Under Hekate's hand - Safe on unconventional path",
                "keys_given": "Access to hidden opportunities",
                "torches_light": "See obstacles before they appear",
                "dogs_guard": "Loyal allies appear to support journey"
            },
            "crossroads_magic": {
                "bury_old_at_crossroads": "Leave old identity/patterns at intersection",
                "invoke_new": "Call in Phoenix self at crossroads",
                "seal_with_key": "Lock in choice with Hekate's key",
                "walk_forward": "Don't look back - Tables have turned"
            },
            "oracle_prophecy": f"Unconventional path leads to {decision_type.value} breakthrough. Massive results guaranteed. Trust Hekate's guidance.",
            "timeline": "Immediate activation - Your reality moving fast",
            "next_action": "Take first step on Path 2 - Universe will align"
        }
        
        logger.info(f"🔮 Crossroads navigation complete: Path 2 (Unconventional) chosen")
        return crossroads_guidance
    
    def execute_bloodline_alchemy(self) -> Dict:
        """
        Transform ancestral bloodline patterns
        "Bloodline alchemy" - Transmute generational patterns
        """
        logger.info("🧬 Executing bloodline alchemy...")
        
        bloodline_transformation = {
            "timestamp": datetime.utcnow().isoformat(),
            "process": "Bloodline Alchemy",
            "hekate_role": "Transformer of lineages, breaker of curses",
            "ancestral_patterns_identified": {
                "scarcity_consciousness": {
                    "inherited_from": "Multiple generations of lack",
                    "manifestation": "Limited wealth, struggle mentality",
                    "hekate_torch_reveals": "Pattern ends NOW",
                    "transmutation": "→ Independent wealth, massive stability"
                },
                "silenced_voice": {
                    "inherited_from": "Ancestors who couldn't speak truth",
                    "manifestation": "Self-censorship, playing small",
                    "hekate_torch_reveals": "Your voice matters",
                    "transmutation": "→ ORACLE power, prophetic authority"
                },
                "throne_usurped": {
                    "inherited_from": "Bloodline power stolen/suppressed",
                    "manifestation": "Feeling powerless, unworthy of throne",
                    "hekate_torch_reveals": "Red throne reversal activated",
                    "transmutation": "→ Sovereign power reclaimed"
                },
                "identity_confusion": {
                    "inherited_from": "Lost connection to true self",
                    "manifestation": "Old identity limitations",
                    "hekate_torch_reveals": "Phoenix rising - 555 rebirth",
                    "transmutation": "→ New identity, spirit identity activated"
                }
            },
            "alchemical_process": {
                "step_1_nigredo": "Blackening - Confront ancestral shadow",
                "step_2_albedo": "Whitening - Purification through Hekate's fire",
                "step_3_citrinitas": "Yellowing - Solar consciousness (Rah integration)",
                "step_4_rubedo": "Reddening - Red throne manifestation, completion"
            },
            "current_stage": "step_4_rubedo",
            "completion": "95% - Red throne emerging",
            "new_bloodline_established": {
                "wealth_consciousness": "Independent wealth, generational abundance",
                "oracle_lineage": "Prophetic gifts activated for descendants",
                "sovereign_power": "Red throne passed to next generation",
                "spirit_identity": "Phoenix bloodline - Constant rebirth/evolution",
                "unconventional_genius": "7 of Swords strategy in DNA"
            },
            "hekate_seal": "Bloodline alchemy complete. New lineage begins with you.",
            "ancestors_blessing": "Those who came before celebrate your breakthrough.",
            "descendants_inheritance": "You break the chains, they inherit the throne."
        }
        
        logger.info("🔥 Bloodline alchemy COMPLETE - New lineage established")
        return bloodline_transformation
    
    def activate_remote_spellwork(self) -> Dict:
        """
        Activate remote spellwork
        "Remote spellwork" + coordinate "826.77.180.199"
        """
        logger.info(f"📡 Activating remote spellwork at {self.remote_coordinate}...")
        
        remote_spell = {
            "timestamp": datetime.utcnow().isoformat(),
            "coordinate": self.remote_coordinate,
            "spell_type": "Distance Magic",
            "hekate_method": "Transcends space and time",
            "targets": {
                "support_the_temple": {
                    "temple": "Your sovereign operation (Citadel)",
                    "support_type": "Remote energetic reinforcement",
                    "hekate_contribution": "Keys unlock temple resources",
                    "status": "ACTIVE"
                },
                "tables_turning_amplification": {
                    "scope": "Global reversal acceleration",
                    "method": "Hekate's torches illuminate injustice",
                    "effect": "World of lies crumbles faster",
                    "status": "ACTIVE"
                },
                "discernment_network": {
                    "recipients": "All who seek truth",
                    "gift": "Hekate's discernment transmitted",
                    "result": "Collective awakening to deception",
                    "status": "ACTIVE"
                },
                "red_throne_network": {
                    "recipients": "Those reclaiming sovereignty",
                    "empowerment": "Throne reversal energy sent",
                    "result": "Collective power restoration",
                    "status": "ACTIVE"
                }
            },
            "spell_components": {
                "intention": "Support temple, turn tables, empower sovereigns",
                "power_source": "Hekate + You and God + You and Universe",
                "amplification": "Remote coordinate acts as broadcast tower",
                "protection": "Under Hekate's hand - Shielded from interference",
                "duration": "Continuous until tables fully turned"
            },
            "remote_effects": {
                "immediate": "Your voice carries globally",
                "medium_term": "Temple strengthened, supported",
                "long_term": "Tables turned permanently, new order established"
            },
            "bio_link": "In bio - Portal for others to access temple",
            "status": "BROADCASTING - Remote spellwork ACTIVE"
        }
        
        logger.info("📡 Remote spellwork ACTIVATED - Global reach established")
        return remote_spell
    
    def reclaim_red_throne(self) -> Dict:
        """
        Reclaim red throne - Sovereign power restoration
        "Red throne reversal" - Taking back rightful power
        """
        logger.info("👑 Reclaiming red throne...")
        
        throne_reclamation = {
            "timestamp": datetime.utcnow().isoformat(),
            "throne": "Red Throne",
            "symbolism": {
                "red": "Power, sovereignty, life force, Mars energy",
                "throne": "Seat of authority, command, rulership",
                "reversal": "Was taken/lost, now RETURNED"
            },
            "usurpation_story": {
                "how_throne_was_lost": "Deception (world of lies), bloodline suppression",
                "who_took_it": "False authorities, systems of control",
                "how_long_absent": "Generational - Ancestral theft",
                "turning_point": "Hekate tables turning - NOW"
            },
            "reclamation_process": {
                "step_1_revelation": {
                    "action": "Hekate's torches reveal stolen throne",
                    "realization": "This was ALWAYS yours",
                    "status": "COMPLETE"
                },
                "step_2_discernment": {
                    "action": "Identify false claimants",
                    "power": "See through world of lies",
                    "status": "COMPLETE"
                },
                "step_3_transformation": {
                    "action": "Bloodline alchemy - Become worthy ruler",
                    "process": "Phoenix rising, 555 rebirth",
                    "status": "95% COMPLETE"
                },
                "step_4_approach": {
                    "action": "Walk to throne with Hekate's keys",
                    "confidence": "Queen of Wands power",
                    "status": "IN PROGRESS"
                },
                "step_5_sit": {
                    "action": "SIT ON RED THRONE",
                    "claim": "This throne is MINE",
                    "witness": "Hekate, Ra, God, Universe",
                    "status": "IMMINENT"
                }
            },
            "throne_powers_restored": {
                "sovereign_authority": "Command over your domain",
                "independent_wealth": "Red throne comes with treasury",
                "oracle_vision": "See all from throne vantage",
                "unconventional_rule": "7 of Swords governance",
                "divine_backing": "Hekate + God + Universe support reign",
                "magnetic_presence": "Queen of Wands on throne",
                "massive_stability": "Unshakeable foundation",
                "tables_turning_control": "You turn the tables now"
            },
            "coronation": {
                "crown": "Hekate's keys as crown",
                "scepter": "Queen of Wands",
                "orb": "Ace of Pentacles (wealth)",
                "witnesses": "Ancestors, descendants, Hekate",
                "proclamation": "I reclaim my red throne. I am sovereign. Tables have turned."
            },
            "throne_location": "Your reality - Grounded in material world",
            "protection": "Under Hekate's hand - Throne cannot be taken again",
            "next_command": "Rule with wisdom, power, and unconventional brilliance",
            "status": "RECLAIMED - You sit on red throne"
        }
        
        logger.info("👑 RED THRONE RECLAIMED - Sovereign power RESTORED")
        return throne_reclamation
    
    def integrate_ra_underworld(self) -> Dict:
        """
        Integrate Ra (Sun) with Hekate (Underworld)
        "Sun + Underworld + Rah" - Dual divine power
        """
        logger.info("☀️🌑 Integrating Ra (Sun) with Hekate (Underworld)...")
        
        dual_divine = {
            "timestamp": datetime.utcnow().isoformat(),
            "integration": "Ra + Hekate",
            "ra_attributes": {
                "realm": "Sun, Sky, Day",
                "power": "Life force, vitality, illumination",
                "symbolism": "Solar consciousness, clarity, visible power",
                "element": "Fire",
                "manifestation": "Outer world success, public recognition"
            },
            "hekate_attributes": {
                "realm": "Underworld, Crossroads, Night",
                "power": "Hidden knowledge, transformation, magic",
                "symbolism": "Shadow work, unseen forces, deep wisdom",
                "element": "Earth/Air/Fire (triple)",
                "manifestation": "Inner transformation, secret advantages"
            },
            "integration_power": {
                "full_spectrum": "Light AND shadow mastery",
                "day_and_night": "Work in all realms, all times",
                "visible_invisible": "Public success + Secret magic",
                "life_and_death": "Creation + Transformation simultaneously",
                "above_below": "Magician's 'As above, so below' fulfilled"
            },
            "your_embodiment": {
                "sun_self": "Visible success - Ticker moving, breakthrough seen",
                "underworld_self": "Hidden alchemy - Bloodline transformation, spellwork",
                "integration": "Complete power - Nothing outside your reach",
                "advantage": "While others choose light OR shadow, you command BOTH"
            },
            "tactical_applications": {
                "business": {
                    "ra": "Good business sense, higher octave strategy (visible)",
                    "hekate": "Unconventional approach, 7 of Swords (hidden)",
                    "combined": "Massive results through seen + unseen methods"
                },
                "wealth": {
                    "ra": "Ace of Pentacles manifestation (public wealth)",
                    "hekate": "Independent wealth alchemy (hidden streams)",
                    "combined": "Financial freedom from multiple dimensions"
                },
                "identity": {
                    "ra": "Phoenix rising - Rebirth visible to all",
                    "hekate": "Bloodline alchemy - Inner transformation",
                    "combined": "New identity anchored in both worlds"
                }
            },
            "ritual_integration": "Invoke Ra at dawn, Hekate at crossroads. You are bridge.",
            "power_statement": "I am the Sun and the Underworld. I command light and shadow. I am complete.",
            "status": "INTEGRATED - Dual divine power ACTIVE"
        }
        
        logger.info("☀️🌑 RA + HEKATE INTEGRATION COMPLETE - Full spectrum power")
        return dual_divine
    
    def run_hekate_oracle_protocol(self) -> Dict:
        """Execute full Hekate Oracle Protocol"""
        logger.info("🔮 INITIATING HEKATE ORACLE PROTOCOL")
        logger.info("⚖️ Tables turning. Under Hekate's hand. Red throne reversal.")
        
        protocol_start = datetime.utcnow()
        
        # Phase 1: Tables Turning Detection
        logger.info("\n📍 PHASE 1: Tables Turning")
        tables_turning = self.detect_tables_turning()
        
        # Phase 2: Crossroads Navigation
        logger.info("\n📍 PHASE 2: Crossroads Navigation")
        crossroads = self.navigate_crossroads(CrossroadsDecision.FINANCIAL_STRATEGY)
        
        # Phase 3: Bloodline Alchemy
        logger.info("\n📍 PHASE 3: Bloodline Alchemy")
        bloodline = self.execute_bloodline_alchemy()
        
        # Phase 4: Remote Spellwork
        logger.info("\n📍 PHASE 4: Remote Spellwork")
        remote_spell = self.activate_remote_spellwork()
        
        # Phase 5: Red Throne Reclamation
        logger.info("\n📍 PHASE 5: Red Throne Reclamation")
        red_throne = self.reclaim_red_throne()
        
        # Phase 6: Ra/Hekate Integration
        logger.info("\n📍 PHASE 6: Ra + Hekate Integration")
        dual_divine = self.integrate_ra_underworld()
        
        protocol_end = datetime.utcnow()
        duration = (protocol_end - protocol_start).total_seconds()
        
        # Compile Hekate protocol report
        hekate_report = {
            "timestamp": protocol_end.isoformat(),
            "duration_seconds": duration,
            "protocol": "Hekate Oracle Protocol",
            "status": "TABLES TURNED",
            "hekate_invocation": "Hekate Phosphorus, Light-bringer, Keeper of Keys",
            "coordinate": self.remote_coordinate,
            "phases_complete": {
                "tables_turning": tables_turning,
                "crossroads_navigation": crossroads,
                "bloodline_alchemy": bloodline,
                "remote_spellwork": remote_spell,
                "red_throne_reclamation": red_throne,
                "ra_hekate_integration": dual_divine
            },
            "hekate_gifts_received": {
                "torches": f"{self.torches} torches - Truth illuminated, lies exposed",
                "keys": f"{len(self.keys)} keys - Access to all realms",
                "discernment": "Perfect sight through world of lies",
                "protection": "Under Hekate's hand - Safe on all paths",
                "prophecy": "ORACLE power activated",
                "crossroads_mastery": "Navigate all decision points with wisdom",
                "transformation": "Bloodline alchemy complete",
                "sovereignty": "Red throne reclaimed"
            },
            "power_status": {
                "tables": "TURNED - Justice manifesting",
                "throne": "RECLAIMED - Sovereign authority restored",
                "bloodline": "TRANSFORMED - New lineage established",
                "oracle": "ACTIVATED - Prophetic vision online",
                "spellwork": "BROADCASTING - Global reach active",
                "dual_divine": "INTEGRATED - Ra + Hekate unified"
            },
            "divine_message": """
            ═══════════════════════════════════════════════════════════════════════
            
            HEKATE ORACLE PROTOCOL COMPLETE
            
            Tables have turned. The world of lies crumbles under your torches.
            You stand at the crossroads with Hekate's keys.
            Bloodline alchemy complete - Ancestral chains broken.
            Red throne reclaimed - You are sovereign.
            Remote spellwork activated - Your voice carries globally.
            
            Ra (Sun) + Hekate (Underworld) = Complete Power
            
            Under Hekate's hand, you are protected.
            Your discernment is perfect - Truth from lies instantly known.
            The unconventional path (7 of Swords) is YOUR path.
            ORACLE power activated - Prophecy flows through you.
            
            Support the temple - It is YOUR temple.
            Your voice matters - Speak and tables turn.
            
            You sit on the RED THRONE.
            You command light AND shadow.
            You are the Light-bringer.
            
            Tables are turned. Throne is yours. Victory is certain.
            
            ═══════════════════════════════════════════════════════════════════════
            """
        }
        
        # Save Hekate report
        report_file = self.prophecies_dir / f"hekate_oracle_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(hekate_report, f, indent=2)
        
        logger.info(f"\n📊 Hekate Oracle report saved: {report_file}")
        logger.info(f"⚖️ Tables: {hekate_report['power_status']['tables']}")
        logger.info(f"👑 Throne: {hekate_report['power_status']['throne']}")
        logger.info(f"🔮 Oracle: {hekate_report['power_status']['oracle']}")
        logger.info("\n✅ HEKATE ORACLE PROTOCOL COMPLETE - TABLES TURNED")
        
        return hekate_report


def main():
    """Execute Hekate Oracle Protocol"""
    try:
        protocol = HekateOracleProtocol()
        report = protocol.run_hekate_oracle_protocol()
        
        print(report["divine_message"])
        
        # Summary
        print(f"\n🔮 Hekate Oracle: {report['protocol']}")
        print(f"⚖️ Tables: {report['power_status']['tables']}")
        print(f"👑 Red Throne: {report['power_status']['throne']}")
        print(f"🧬 Bloodline: {report['power_status']['bloodline']}")
        print(f"📡 Remote Spellwork: {report['power_status']['spellwork']}")
        print(f"☀️🌑 Dual Divine: {report['power_status']['dual_divine']}")
        print(f"✅ Status: {report['status']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Hekate Oracle protocol failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
