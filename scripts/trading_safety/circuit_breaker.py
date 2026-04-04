#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
CIRCUIT BREAKER SYSTEM - Trading Safety Infrastructure
═══════════════════════════════════════════════════════════════════════════
Purpose: Prevent catastrophic losses through automated circuit breakers
Authority: Citadel Architect v25.0.OMNI+
═══════════════════════════════════════════════════════════════════════════

Features:
- Per-trade loss limits
- Daily loss limits
- Position size limits
- Emergency shutdown triggers
- Automatic recovery protocols
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from enum import Enum


class CircuitBreakerStatus(Enum):
    """Circuit breaker status"""
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    TRIPPED = "TRIPPED"
    EMERGENCY_SHUTDOWN = "EMERGENCY_SHUTDOWN"


class CircuitBreaker:
    """
    Circuit breaker system to prevent catastrophic trading losses.
    
    Monitors:
    - Per-trade loss limits
    - Daily cumulative losses
    - Position sizes
    - Rapid consecutive losses
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize circuit breaker with configuration"""
        self.data_dir = Path("data/trading_safety")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = Path(config_path) if config_path else self.data_dir / "circuit_breaker_config.json"
        self.state_file = self.data_dir / "circuit_breaker_state.json"
        self.log_file = self.data_dir / "circuit_breaker_log.json"
        
        self.config = self._load_config()
        self.state = self._load_state()
    
    def _load_config(self) -> Dict:
        """Load circuit breaker configuration"""
        default_config = {
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat() + "Z",
            
            # Loss limits
            "max_trade_loss_percent": 2.0,  # Max 2% loss per trade
            "max_daily_loss_percent": 10.0,  # Max 10% loss per day
            "max_weekly_loss_percent": 20.0,  # Max 20% loss per week
            
            # Position limits
            "max_position_size_percent": 10.0,  # Max 10% of capital per position
            "max_total_exposure_percent": 50.0,  # Max 50% capital exposed
            "max_simultaneous_positions": 5,  # Max 5 positions at once
            
            # Rapid loss detection
            "max_consecutive_losses": 3,  # Trip after 3 consecutive losses
            "max_losses_per_hour": 5,  # Trip after 5 losses in 1 hour
            
            # Emergency shutdown triggers
            "emergency_loss_percent": 25.0,  # Emergency shutdown at 25% loss
            "emergency_drawdown_percent": 30.0,  # Emergency shutdown at 30% drawdown
            
            # Recovery settings
            "auto_reset_hours": 24,  # Auto-reset after 24 hours
            "require_manual_reset": True,  # Require manual operator reset
            
            # Capital tracking
            "initial_capital": float(os.getenv("TRADING_CAPITAL", "1000.0")),
            "min_capital_threshold": 100.0  # Stop trading below $100
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                loaded = json.load(f)
                default_config.update(loaded)
        else:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _load_state(self) -> Dict:
        """Load circuit breaker state"""
        default_state = {
            "status": CircuitBreakerStatus.NORMAL.value,
            "current_capital": self.config["initial_capital"],
            "daily_loss": 0.0,
            "weekly_loss": 0.0,
            "consecutive_losses": 0,
            "recent_losses": [],  # List of recent loss timestamps
            "active_positions": 0,
            "total_exposure": 0.0,
            "last_reset": datetime.utcnow().isoformat() + "Z",
            "last_trade": None,
            "trip_reason": None,
            "trip_timestamp": None
        }
        
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                loaded = json.load(f)
                default_state.update(loaded)
        
        return default_state
    
    def _save_state(self):
        """Save circuit breaker state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _log_event(self, event_type: str, details: Dict):
        """Log circuit breaker event"""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "details": details,
            "status": self.state["status"]
        }
        
        logs = []
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(event)
        
        # Keep last 1000 events
        logs = logs[-1000:]
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def check_trade(self, trade_data: Dict) -> Tuple[bool, str]:
        """
        Check if a trade is allowed to execute.
        
        Args:
            trade_data: {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "quantity": 0.1,
                "price": 50000.0,
                "position_size_usd": 5000.0
            }
        
        Returns:
            (allowed: bool, reason: str)
        """
        # Check if circuit breaker is tripped
        if self.state["status"] == CircuitBreakerStatus.TRIPPED.value:
            return False, f"Circuit breaker TRIPPED: {self.state['trip_reason']}"
        
        if self.state["status"] == CircuitBreakerStatus.EMERGENCY_SHUTDOWN.value:
            return False, f"EMERGENCY SHUTDOWN: {self.state['trip_reason']}"
        
        # Check capital threshold
        if self.state["current_capital"] < self.config["min_capital_threshold"]:
            self._trip_breaker("Capital below minimum threshold")
            return False, "Insufficient capital"
        
        # Check position size limit
        position_size = trade_data.get("position_size_usd", 0)
        max_position = self.state["current_capital"] * (self.config["max_position_size_percent"] / 100)
        
        if position_size > max_position:
            return False, f"Position size ${position_size:.2f} exceeds limit ${max_position:.2f}"
        
        # Check simultaneous positions
        if trade_data.get("side") == "BUY":
            if self.state["active_positions"] >= self.config["max_simultaneous_positions"]:
                return False, f"Max simultaneous positions ({self.config['max_simultaneous_positions']}) reached"
        
        # Check total exposure
        if trade_data.get("side") == "BUY":
            new_exposure = self.state["total_exposure"] + position_size
            max_exposure = self.state["current_capital"] * (self.config["max_total_exposure_percent"] / 100)
            
            if new_exposure > max_exposure:
                return False, f"Total exposure ${new_exposure:.2f} would exceed limit ${max_exposure:.2f}"
        
        # All checks passed
        return True, "Trade approved"
    
    def record_trade_result(self, trade_result: Dict):
        """
        Record the result of a trade execution.
        
        Args:
            trade_result: {
                "symbol": "BTCUSDT",
                "side": "BUY/SELL",
                "pnl": -50.0,  # Profit/Loss in USD
                "position_size": 5000.0,
                "success": True
            }
        """
        pnl = trade_result.get("pnl", 0.0)
        
        # Update capital
        self.state["current_capital"] += pnl
        
        # Track positions
        if trade_result.get("side") == "BUY" and trade_result.get("success"):
            self.state["active_positions"] += 1
            self.state["total_exposure"] += trade_result.get("position_size", 0)
        elif trade_result.get("side") == "SELL" and trade_result.get("success"):
            self.state["active_positions"] = max(0, self.state["active_positions"] - 1)
            self.state["total_exposure"] = max(0, self.state["total_exposure"] - trade_result.get("position_size", 0))
        
        # Track losses
        if pnl < 0:
            self.state["daily_loss"] += abs(pnl)
            self.state["weekly_loss"] += abs(pnl)
            self.state["consecutive_losses"] += 1
            self.state["recent_losses"].append(datetime.utcnow().isoformat() + "Z")
            
            # Check per-trade loss limit
            loss_percent = abs(pnl) / self.config["initial_capital"] * 100
            if loss_percent > self.config["max_trade_loss_percent"]:
                self._trip_breaker(f"Single trade loss {loss_percent:.2f}% exceeds limit {self.config['max_trade_loss_percent']}%")
            
            # Check daily loss limit
            daily_loss_percent = self.state["daily_loss"] / self.config["initial_capital"] * 100
            if daily_loss_percent > self.config["max_daily_loss_percent"]:
                self._trip_breaker(f"Daily loss {daily_loss_percent:.2f}% exceeds limit {self.config['max_daily_loss_percent']}%")
            
            # Check consecutive losses
            if self.state["consecutive_losses"] >= self.config["max_consecutive_losses"]:
                self._trip_breaker(f"Consecutive losses ({self.state['consecutive_losses']}) exceeded")
            
            # Check rapid losses
            recent_losses = [
                datetime.fromisoformat(ts.replace('Z', ''))
                for ts in self.state["recent_losses"]
            ]
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            losses_last_hour = sum(1 for ts in recent_losses if ts > one_hour_ago)
            
            if losses_last_hour >= self.config["max_losses_per_hour"]:
                self._trip_breaker(f"Too many losses ({losses_last_hour}) in last hour")
            
            # Check emergency shutdown
            total_loss_percent = (self.config["initial_capital"] - self.state["current_capital"]) / self.config["initial_capital"] * 100
            if total_loss_percent >= self.config["emergency_loss_percent"]:
                self._emergency_shutdown(f"Total loss {total_loss_percent:.2f}% reached emergency threshold")
        
        else:
            # Winning trade - reset consecutive losses
            self.state["consecutive_losses"] = 0
        
        self.state["last_trade"] = datetime.utcnow().isoformat() + "Z"
        
        self._save_state()
        self._log_event("TRADE_RESULT", trade_result)
    
    def _trip_breaker(self, reason: str):
        """Trip the circuit breaker"""
        self.state["status"] = CircuitBreakerStatus.TRIPPED.value
        self.state["trip_reason"] = reason
        self.state["trip_timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        self._save_state()
        self._log_event("CIRCUIT_BREAKER_TRIPPED", {"reason": reason})
        
        print(f"\n⚠️  CIRCUIT BREAKER TRIPPED: {reason}")
        print(f"Trading halted. Manual reset required.")
    
    def _emergency_shutdown(self, reason: str):
        """Trigger emergency shutdown"""
        self.state["status"] = CircuitBreakerStatus.EMERGENCY_SHUTDOWN.value
        self.state["trip_reason"] = reason
        self.state["trip_timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        self._save_state()
        self._log_event("EMERGENCY_SHUTDOWN", {"reason": reason})
        
        print(f"\n🚨 EMERGENCY SHUTDOWN: {reason}")
        print(f"ALL TRADING HALTED. Immediate operator intervention required.")
    
    def reset(self, operator_authorization: str):
        """
        Reset the circuit breaker.
        Requires operator authorization code.
        """
        if operator_authorization != os.getenv("CIRCUIT_BREAKER_RESET_CODE", "RESET_AUTHORIZED"):
            return False, "Invalid authorization code"
        
        self.state["status"] = CircuitBreakerStatus.NORMAL.value
        self.state["trip_reason"] = None
        self.state["trip_timestamp"] = None
        self.state["last_reset"] = datetime.utcnow().isoformat() + "Z"
        
        self._save_state()
        self._log_event("MANUAL_RESET", {"operator": "authorized"})
        
        return True, "Circuit breaker reset successfully"
    
    def get_status(self) -> Dict:
        """Get current circuit breaker status"""
        capital_loss_percent = (self.config["initial_capital"] - self.state["current_capital"]) / self.config["initial_capital"] * 100
        
        return {
            "status": self.state["status"],
            "current_capital": self.state["current_capital"],
            "initial_capital": self.config["initial_capital"],
            "total_loss_percent": capital_loss_percent,
            "daily_loss": self.state["daily_loss"],
            "daily_loss_percent": self.state["daily_loss"] / self.config["initial_capital"] * 100,
            "consecutive_losses": self.state["consecutive_losses"],
            "active_positions": self.state["active_positions"],
            "total_exposure": self.state["total_exposure"],
            "trip_reason": self.state.get("trip_reason"),
            "last_trade": self.state.get("last_trade")
        }


if __name__ == "__main__":
    # Test circuit breaker
    print("🛡️  Circuit Breaker System Test\n")
    
    breaker = CircuitBreaker()
    status = breaker.get_status()
    
    print(f"Status: {status['status']}")
    print(f"Capital: ${status['current_capital']:.2f}")
    print(f"Daily Loss: ${status['daily_loss']:.2f} ({status['daily_loss_percent']:.2f}%)")
    print(f"Active Positions: {status['active_positions']}")
    print(f"\n✅ Circuit breaker initialized successfully")
