#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
HARVEST MOON TRADER — The Quant-Hub (v22.2121)
═══════════════════════════════════════════════════════════════════════════
Purpose: XRP/Ripple trading intelligence with 4-module architecture
Authority: Admiral Chance M.S. — OMNI-TIA Vascular Expansion
Integration: PvC Ledger forensic logging, Citadel Dashboard API

Modules:
  - SniperModule:      High-frequency entry/exit (56% OI Spike)
  - TrendModule:       Long-term vascular alignment (July 4th Reset)
  - VolatilityModule:  Micro-oscillation management ($1.39–$1.56)
  - CommanderModule:   Orchestrator & Citadel Dashboard API
═══════════════════════════════════════════════════════════════════════════
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

STABILITY_CONSTANT = 9293
SYNC_FREQUENCY_HZ = 144
ASSET_SYMBOL = "XRP"

# OI Spike threshold from PeaceVortex data
OI_SPIKE_THRESHOLD = 0.56  # 56%

# July 4th Reset long-term targets
JULY4_RESET_TARGETS = {
    "conservative": 1.90,
    "moderate": 3.50,
    "aggressive": 5.00,
}

# Micro-oscillation range
VOLATILITY_FLOOR = 1.39
VOLATILITY_CEILING = 1.56

# Relative paths only — Stainless Pipeline Rule #1
LEDGER_DIR = Path("./data/trading/ledger")
TRADE_LOG_DIR = Path("./data/trading/logs")

logger = logging.getLogger("harvest_moon")


class TradeAction(Enum):
    """Possible trade actions."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    SCALE_IN = "SCALE_IN"
    SCALE_OUT = "SCALE_OUT"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    CAUTION = "CAUTION"
    CRITICAL = "CRITICAL"
    VASCULAR_THRESHOLD = "VASCULAR_THRESHOLD"


@dataclass
class MarketSnapshot:
    """Point-in-time market data for XRP."""
    price: float
    open_interest: float = 0.0
    oi_change_pct: float = 0.0
    volume_24h: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class TradeSignal:
    """A signal produced by any module."""
    action: TradeAction
    module: str
    confidence: float  # 0.0 – 1.0
    price: float
    reason: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict = field(default_factory=dict)


@dataclass
class TradeRecord:
    """Immutable trade record logged to the PvC Ledger."""
    trade_id: str
    action: str
    price: float
    quantity: float
    module: str
    reason: str
    timestamp: str
    pvc_logged: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 1: SNIPER MODULE — High-Frequency Entry/Exit
# ═══════════════════════════════════════════════════════════════════════════

class SniperModule:
    """
    High-frequency entry/exit logic based on the 56% OI Spike
    data from the PeaceVortex.

    When open interest spikes ≥56%, the Sniper identifies momentum
    entries and exits with tight risk parameters.
    """

    MODULE_NAME = "SniperModule"

    def __init__(self, oi_threshold: float = OI_SPIKE_THRESHOLD):
        self.oi_threshold = oi_threshold
        self.active_positions: list[dict] = []
        logger.info("[SNIPER] Module initialised — OI threshold %.0f%%",
                     oi_threshold * 100)

    def analyse(self, snapshot: MarketSnapshot) -> Optional[TradeSignal]:
        """Analyse a market snapshot and produce a signal if conditions met."""
        if snapshot.oi_change_pct >= self.oi_threshold:
            return TradeSignal(
                action=TradeAction.BUY,
                module=self.MODULE_NAME,
                confidence=min(snapshot.oi_change_pct / 1.0, 1.0),
                price=snapshot.price,
                reason=(
                    f"OI spike detected: {snapshot.oi_change_pct:.1%} "
                    f"≥ threshold {self.oi_threshold:.0%} — PeaceVortex entry"
                ),
                metadata={
                    "oi_change_pct": snapshot.oi_change_pct,
                    "volume_24h": snapshot.volume_24h,
                },
            )

        if snapshot.oi_change_pct <= -self.oi_threshold:
            return TradeSignal(
                action=TradeAction.SELL,
                module=self.MODULE_NAME,
                confidence=min(abs(snapshot.oi_change_pct) / 1.0, 1.0),
                price=snapshot.price,
                reason=(
                    f"OI dump detected: {snapshot.oi_change_pct:.1%} "
                    f"— exit triggered"
                ),
                metadata={
                    "oi_change_pct": snapshot.oi_change_pct,
                    "volume_24h": snapshot.volume_24h,
                },
            )

        return None  # No actionable signal

    def status(self) -> dict:
        """Return module status."""
        return {
            "module": self.MODULE_NAME,
            "oi_threshold": self.oi_threshold,
            "active_positions": len(self.active_positions),
            "status": "ONLINE",
        }


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 2: TREND MODULE — Long-Term Vascular Alignment
# ═══════════════════════════════════════════════════════════════════════════

class TrendModule:
    """
    Long-term vascular alignment based on the July 4th Reset targets.

    Evaluates whether price is approaching key long-term milestones
    and recommends position-sizing adjustments.
    """

    MODULE_NAME = "TrendModule"

    def __init__(self, targets: Optional[dict] = None):
        self.targets = targets or JULY4_RESET_TARGETS
        self.trend_history: list[dict] = []
        logger.info("[TREND] Module initialised — targets: %s", self.targets)

    def analyse(self, snapshot: MarketSnapshot) -> Optional[TradeSignal]:
        """Evaluate price against July 4th Reset milestones."""
        price = snapshot.price

        # Check proximity to each target level
        for level_name, target_price in sorted(
            self.targets.items(), key=lambda x: x[1]
        ):
            distance_pct = (target_price - price) / target_price if target_price else 0

            if 0 < distance_pct <= 0.05:
                # Within 5% of target — scale-in opportunity
                return TradeSignal(
                    action=TradeAction.SCALE_IN,
                    module=self.MODULE_NAME,
                    confidence=0.7 + (0.3 * (1 - distance_pct)),
                    price=price,
                    reason=(
                        f"Price ${price:.4f} within {distance_pct:.1%} "
                        f"of {level_name} target ${target_price:.2f} "
                        f"— July 4th Reset alignment"
                    ),
                    metadata={
                        "target_level": level_name,
                        "target_price": target_price,
                        "distance_pct": distance_pct,
                    },
                )

            if distance_pct < 0:
                # Target exceeded — partial exit
                return TradeSignal(
                    action=TradeAction.SCALE_OUT,
                    module=self.MODULE_NAME,
                    confidence=0.8,
                    price=price,
                    reason=(
                        f"Price ${price:.4f} exceeded {level_name} "
                        f"target ${target_price:.2f} — scale-out signal"
                    ),
                    metadata={
                        "target_level": level_name,
                        "target_price": target_price,
                        "exceeded_by_pct": abs(distance_pct),
                    },
                )

        return None

    def status(self) -> dict:
        """Return module status."""
        return {
            "module": self.MODULE_NAME,
            "targets": self.targets,
            "history_entries": len(self.trend_history),
            "status": "ONLINE",
        }


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 3: VOLATILITY MODULE — Micro-Oscillation Management
# ═══════════════════════════════════════════════════════════════════════════

class VolatilityModule:
    """
    Manages micro-oscillations between $1.39 and $1.56.

    Uses a range-bound strategy: buy near the floor, sell near
    the ceiling, hold in the middle band.
    """

    MODULE_NAME = "VolatilityModule"

    def __init__(
        self,
        floor: float = VOLATILITY_FLOOR,
        ceiling: float = VOLATILITY_CEILING,
    ):
        self.floor = floor
        self.ceiling = ceiling
        self.midpoint = (floor + ceiling) / 2
        self.band_width = ceiling - floor
        logger.info(
            "[VOLATILITY] Module initialised — range $%.2f–$%.2f",
            floor, ceiling,
        )

    def analyse(self, snapshot: MarketSnapshot) -> Optional[TradeSignal]:
        """Evaluate price within the micro-oscillation band."""
        price = snapshot.price

        # Below floor — strong buy zone
        if price <= self.floor:
            return TradeSignal(
                action=TradeAction.BUY,
                module=self.MODULE_NAME,
                confidence=0.9,
                price=price,
                reason=(
                    f"Price ${price:.4f} at/below volatility floor "
                    f"${self.floor:.2f} — accumulation zone"
                ),
                metadata={"zone": "floor", "band_position": 0.0},
            )

        # Near floor (bottom 20% of band)
        band_position = (price - self.floor) / self.band_width if self.band_width else 0
        if band_position <= 0.20:
            return TradeSignal(
                action=TradeAction.BUY,
                module=self.MODULE_NAME,
                confidence=0.7,
                price=price,
                reason=(
                    f"Price ${price:.4f} in lower band "
                    f"(position {band_position:.0%}) — buy zone"
                ),
                metadata={"zone": "lower_band", "band_position": band_position},
            )

        # Near ceiling (top 20% of band)
        if band_position >= 0.80:
            return TradeSignal(
                action=TradeAction.SELL,
                module=self.MODULE_NAME,
                confidence=0.7,
                price=price,
                reason=(
                    f"Price ${price:.4f} in upper band "
                    f"(position {band_position:.0%}) — take-profit zone"
                ),
                metadata={"zone": "upper_band", "band_position": band_position},
            )

        # Above ceiling — strong sell zone
        if price >= self.ceiling:
            return TradeSignal(
                action=TradeAction.SELL,
                module=self.MODULE_NAME,
                confidence=0.9,
                price=price,
                reason=(
                    f"Price ${price:.4f} at/above volatility ceiling "
                    f"${self.ceiling:.2f} — distribution zone"
                ),
                metadata={"zone": "ceiling", "band_position": 1.0},
            )

        # Middle band — hold
        return TradeSignal(
            action=TradeAction.HOLD,
            module=self.MODULE_NAME,
            confidence=0.5,
            price=price,
            reason=(
                f"Price ${price:.4f} in neutral zone "
                f"(position {band_position:.0%}) — hold"
            ),
            metadata={"zone": "neutral", "band_position": band_position},
        )

    def status(self) -> dict:
        """Return module status."""
        return {
            "module": self.MODULE_NAME,
            "floor": self.floor,
            "ceiling": self.ceiling,
            "midpoint": self.midpoint,
            "band_width": self.band_width,
            "status": "ONLINE",
        }


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 4: COMMANDER MODULE — Orchestrator & Dashboard API
# ═══════════════════════════════════════════════════════════════════════════

class CommanderModule:
    """
    Orchestrates SniperModule, TrendModule, and VolatilityModule.

    Acts as the primary API for the Citadel Dashboard.  All trade
    signals are aggregated, ranked, and logged to the PvC Ledger
    for forensic accountability.
    """

    MODULE_NAME = "CommanderModule"

    def __init__(self):
        self.sniper = SniperModule()
        self.trend = TrendModule()
        self.volatility = VolatilityModule()
        self._trade_counter = 0
        self.trade_history: list[TradeRecord] = []

        # Ensure log directories exist (relative paths)
        LEDGER_DIR.mkdir(parents=True, exist_ok=True)
        TRADE_LOG_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("[COMMANDER] Harvest Moon Trader ONLINE — "
                     "Stability %d, Frequency %dHz",
                     STABILITY_CONSTANT, SYNC_FREQUENCY_HZ)

    # ───────────────────────────────────────────────────────────────────
    # Core Analysis Pipeline
    # ───────────────────────────────────────────────────────────────────

    def evaluate(self, snapshot: MarketSnapshot) -> dict:
        """
        Run all three sub-modules against the current snapshot.

        Returns a unified evaluation with the recommended action,
        individual module signals, and a composite confidence score.
        """
        signals: list[TradeSignal] = []

        for module in (self.sniper, self.trend, self.volatility):
            sig = module.analyse(snapshot)
            if sig is not None:
                signals.append(sig)

        if not signals:
            return {
                "recommended_action": TradeAction.HOLD.value,
                "composite_confidence": 0.0,
                "signals": [],
                "snapshot": asdict(snapshot),
                "stability_constant": STABILITY_CONSTANT,
            }

        # Weight: Sniper 40%, Trend 35%, Volatility 25%
        weight_map = {
            SniperModule.MODULE_NAME: 0.40,
            TrendModule.MODULE_NAME: 0.35,
            VolatilityModule.MODULE_NAME: 0.25,
        }

        weighted_sum = 0.0
        total_weight = 0.0
        action_votes: dict[str, float] = {}

        for sig in signals:
            w = weight_map.get(sig.module, 0.25)
            weighted_sum += sig.confidence * w
            total_weight += w
            action_key = sig.action.value
            action_votes[action_key] = action_votes.get(action_key, 0) + w

        composite_confidence = weighted_sum / total_weight if total_weight else 0
        recommended_action = max(action_votes, key=action_votes.get)  # type: ignore[arg-type]

        return {
            "recommended_action": recommended_action,
            "composite_confidence": round(composite_confidence, 4),
            "signals": [asdict(s) for s in signals],
            "snapshot": asdict(snapshot),
            "stability_constant": STABILITY_CONSTANT,
            "sync_frequency_hz": SYNC_FREQUENCY_HZ,
        }

    # ───────────────────────────────────────────────────────────────────
    # Trade Execution & PvC Ledger Logging
    # ───────────────────────────────────────────────────────────────────

    def execute_trade(
        self,
        action: TradeAction,
        price: float,
        quantity: float,
        reason: str,
        module: str = "CommanderModule",
    ) -> TradeRecord:
        """
        Execute a trade and log it to the PvC Ledger.

        All trades are immutably recorded for forensic accountability.
        """
        self._trade_counter += 1
        trade_id = (
            f"HM-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            f"-{self._trade_counter:04d}"
        )

        record = TradeRecord(
            trade_id=trade_id,
            action=action.value,
            price=price,
            quantity=quantity,
            module=module,
            reason=reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Log to PvC Ledger
        record.pvc_logged = self._log_to_pvc_ledger(record)
        self.trade_history.append(record)

        # Persist trade log
        self._persist_trade_log(record)

        logger.info("[COMMANDER] Trade executed: %s %s @ $%.4f x %.4f — %s",
                     record.action, ASSET_SYMBOL, price, quantity, trade_id)
        return record

    def _log_to_pvc_ledger(self, record: TradeRecord) -> bool:
        """Log trade to PvC Ledger for forensic accountability."""
        ledger_file = LEDGER_DIR / "harvest_moon_trades.json"
        try:
            entries = []
            if ledger_file.exists():
                entries = json.loads(ledger_file.read_text())
            entries.append(asdict(record))
            ledger_file.write_text(json.dumps(entries, indent=2))
            return True
        except Exception as exc:
            logger.error("[COMMANDER] PvC ledger write failed: %s", exc)
            return False

    def _persist_trade_log(self, record: TradeRecord) -> None:
        """Persist trade to daily log file."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = TRADE_LOG_DIR / f"trades_{today}.json"
        try:
            entries = []
            if log_file.exists():
                entries = json.loads(log_file.read_text())
            entries.append(asdict(record))
            log_file.write_text(json.dumps(entries, indent=2))
        except Exception as exc:
            logger.error("[COMMANDER] Trade log write failed: %s", exc)

    # ───────────────────────────────────────────────────────────────────
    # Vascular Threshold Alerts
    # ───────────────────────────────────────────────────────────────────

    def check_vascular_thresholds(self, snapshot: MarketSnapshot) -> list[dict]:
        """
        Check the primary vascular threshold alerts.

        Monitors: $1.90 XRP price node and key target levels.
        """
        alerts = []
        price = snapshot.price
        vascular_node = 1.90

        if price >= vascular_node:
            alerts.append({
                "level": AlertLevel.VASCULAR_THRESHOLD.value,
                "message": (
                    f"$1.90 Vascular Node BREACHED — XRP at ${price:.4f}"
                ),
                "price": price,
                "node": vascular_node,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        for level_name, target in JULY4_RESET_TARGETS.items():
            distance = abs(price - target) / target if target else 0
            if distance <= 0.02:  # Within 2%
                alerts.append({
                    "level": AlertLevel.CRITICAL.value,
                    "message": (
                        f"Approaching {level_name} target "
                        f"${target:.2f} — current ${price:.4f}"
                    ),
                    "price": price,
                    "target": target,
                    "distance_pct": distance,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

        return alerts

    # ───────────────────────────────────────────────────────────────────
    # Dashboard API
    # ───────────────────────────────────────────────────────────────────

    def dashboard_status(self) -> dict:
        """Return full system status for the Citadel Dashboard."""
        return {
            "system": "Harvest Moon Trader",
            "version": "v22.2121",
            "asset": ASSET_SYMBOL,
            "stability_constant": STABILITY_CONSTANT,
            "sync_frequency_hz": SYNC_FREQUENCY_HZ,
            "modules": {
                "sniper": self.sniper.status(),
                "trend": self.trend.status(),
                "volatility": self.volatility.status(),
            },
            "total_trades": len(self.trade_history),
            "status": "ONLINE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# MAIN — Boot Sequence
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Boot the Harvest Moon Trader and run a diagnostic cycle."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("🌙 HARVEST MOON TRADER — Ignition Sequence")
    print("=" * 60)

    commander = CommanderModule()

    # Diagnostic snapshot
    test_snapshot = MarketSnapshot(
        price=1.45,
        open_interest=2_500_000,
        oi_change_pct=0.12,
        volume_24h=850_000_000,
    )

    print(f"\n📊 Test Snapshot: XRP @ ${test_snapshot.price:.4f}")
    evaluation = commander.evaluate(test_snapshot)
    print(f"   Recommended: {evaluation['recommended_action']}")
    print(f"   Confidence:  {evaluation['composite_confidence']:.1%}")
    print(f"   Signals:     {len(evaluation['signals'])}")

    # Check vascular thresholds
    alerts = commander.check_vascular_thresholds(test_snapshot)
    if alerts:
        print(f"\n🚨 Vascular Alerts: {len(alerts)}")
        for alert in alerts:
            print(f"   [{alert['level']}] {alert['message']}")
    else:
        print("\n✅ No vascular threshold breaches")

    # Dashboard status
    status = commander.dashboard_status()
    print(f"\n🏛️ System: {status['system']} {status['version']}")
    print(f"   Stability: {status['stability_constant']}")
    print(f"   Frequency: {status['sync_frequency_hz']}Hz")
    for name, mod in status["modules"].items():
        print(f"   {name}: {mod['status']}")

    print("\n🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors")


if __name__ == "__main__":
    main()
