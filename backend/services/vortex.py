from typing import Dict, List, Optional, Tuple, Any, Union
import os, asyncio, json, logging, time
import ccxt.async_support as ccxt
from datetime import datetime
from huggingface_hub import HfApi

# Setup [T.I.A.] Logger
logger = logging.getLogger("vortex")

class VortexBerserker:
    # Trading constants
    BANKING_FLOW_THRESHOLD = -1.0  # BTC/USDT percentage threshold for positive flow
    SNIPER_PROFIT_TARGET = 1.015   # 1.5% profit target for Sniper trades
    PIRANHA_PROFIT_TARGET = 1.004  # 0.4% profit target for Piranha trades
    HARVESTER_PULLBACK = 0.985     # 1.5% pullback from peak for Harvester exit
    
    def __init__(self):
        # 1. FLEET CONFIGURATION (2/3/1/1 Split)
        self.PIRANHA_SLOTS = [1, 2]         # 0.4% Scalps
        self.HARVESTER_SLOTS = [3, 4, 5]    # Trailing Grids
        self.SNIPER_SLOT = [6]              # Precision Entry (EMA/Vol)
        self.BANKING_SLOT = [7]             # Whale Watcher / Flow Guard
        
        self.base_stake = 8.00
        self.stop_loss_pct = 0.015
        self.max_slots = 7
        
        # Trading universe - reserved for future slot assignment logic
        self.universe = ['SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'ADA/USDT', 'PEPE/USDT', 'PEOPLE/USDT', 'SUI/USDT']
        
        # 2. EXCHANGE & SECURITY
        self.api_key = os.getenv('MEXC_API_KEY')
        self.secret = os.getenv('MEXC_SECRET_KEY')  # Matches main.py convention
        self.mexc = ccxt.mexc({
            'apiKey': self.api_key,
            'secret': self.secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # Blacklist - reserved for future symbol filtering logic
        self.blacklisted = set(['PENGUIN/USDT'])
        
        # 3. STATE & UPLINKS
        self.active_trades = {}
        self.hf_api = HfApi()
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.hf_repo = os.getenv("HUGGINGFACE_REPO")
        self.shadow_path = os.getenv("SHADOW_ARCHIVE_PATH", "/tmp/airgap")
        self.banking_flow = 0.5 # Neutral start
        
        # Backward compatibility attributes
        self.running = False
        self.pulse_interval = 2
        self.scalp_slots = len(self.PIRANHA_SLOTS)
        self.grid_slots = len(self.HARVESTER_SLOTS)
        self.slots = []  # Legacy attribute for compatibility
        self.stake_amount = self.base_stake
        self.default_pulse_interval = 2
        self.throttled_pulse_interval = 4
        self.is_throttled = False
        self.throttle_count = 0
        self.scalp_take_profit = 0.004
        self.grid_trail_step = 0.005
        self.grid_exit_pullback = 0.015
        self.throttle_recovery_wait = 60

    def _log(self, msg: str) -> None:
        formatted = f"[T.I.A.] {msg}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {formatted}")
        logger.info(formatted)

    async def _push_to_huggingface(self, trade_data):
        if self.hf_token and self.hf_repo:
            try:
                self.hf_api.upload_file(
                    path_or_fileobj=json.dumps(trade_data).encode(),
                    path_in_repo=f"trades/{datetime.now().timestamp()}.json",
                    repo_id=self.hf_repo,
                    token=self.hf_token
                )
            except Exception as e:
                self._log(f"⚠️ HF UPLINK FAIL: {e}")

    async def _secure_airgap_dump(self, trade_data):
        try:
            os.makedirs(self.shadow_path, exist_ok=True)
            with open(f"{self.shadow_path}/trades.jsonl", "a") as f:
                f.write(json.dumps(trade_data) + "\n")
        except Exception as e:
            self._log(f"⚠️ AIRGAP FAIL: {e}")

    async def analyze_banking_flow(self):
        """Wing D: Slot 7 - Monitors global USDT flow to block risky buys."""
        try:
            # Simplified flow analysis for pulse
            ticker = await self.mexc.fetch_ticker('BTC/USDT')
            self.banking_flow = 1.0 if ticker['percentage'] > self.BANKING_FLOW_THRESHOLD else -1.0
            if self.banking_flow < 0:
                self._log("🛡️ BANKING SENTRY: Negative flow detected. Buys throttled.")
        except Exception as e:
            self._log(f"⚠️ BANKING FLOW CHECK FAIL: {e}")

    async def pulse_monitor(self):
        """The 2-second pulse monitoring exits and rungs."""
        for slot, trade in list(self.active_trades.items()):
            try:
                ticker = await self.mexc.fetch_ticker(trade['symbol'])
                curr = ticker['last']
                
                # SNIPER/PIRANHA Logic
                if trade['wing'] == "SNIPER" or trade['wing'] == "PIRANHA":
                    target = self.SNIPER_PROFIT_TARGET if trade['wing'] == "SNIPER" else self.PIRANHA_PROFIT_TARGET
                    if curr >= trade['entry'] * target:
                        await self.execute_exit(slot, "💰 PROFIT")
                    elif curr <= trade['entry'] * (1 - self.stop_loss_pct):
                        await self.execute_exit(slot, "🛡️ STOP LOSS")

                # HARVESTER Trailing
                elif trade['wing'] == "HARVESTER":
                    if curr > trade['peak']: trade['peak'] = curr
                    if curr <= trade['peak'] * self.HARVESTER_PULLBACK:
                        await self.execute_exit(slot, "🌾 HARVEST")
            except Exception as e:
                self._log(f"⚠️ MONITOR FAIL {slot}: {e}")

    async def execute_exit(self, slot_id, reason):
        trade = self.active_trades[slot_id]
        symbol = trade['symbol']
        try:
            # Sync-Guard: Verify balance before clearing
            bal = await self.mexc.fetch_balance()
            coin = symbol.split('/')[0]
            if bal.get(coin, {}).get('free', 0) > 0:
                await self.mexc.create_market_sell_order(symbol, trade['qty'])
                self._log(f"✅ {reason}: {symbol} closed at {slot_id}")
                await self._push_to_huggingface(trade)
                await self._secure_airgap_dump(trade)
            del self.active_trades[slot_id]
        except Exception as e:
            # MEXC error code 30005: Order not found / insufficient balance
            if "30005" in str(e):
                del self.active_trades[slot_id]
            self._log(f"❌ EXIT ERROR: {e}")

    async def start(self):
        self.running = True
        self._log("🔥 VORTEX V2 RESTORED: 2 PIRANHAS // 3 HARVESTERS // 1 SNIPER // 1 BANKING.")
        while self.running:
            try:
                await self.analyze_banking_flow()
                # Slot management logic would continue here...
                await self.pulse_monitor()
                await asyncio.sleep(2)
            except Exception as e:
                self._log(f"💀 ENGINE RECOVERY: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the trading engine"""
        self.running = False
        self._log("🛑 Vortex V2 stopped")
    
    async def heartbeat(self):
        """Heartbeat method for compatibility with main.py"""
        await self.analyze_banking_flow()
        await self.pulse_monitor()
    
    async def get_telemetry(self):
        """Get telemetry data for API compatibility"""
        active_slots = len(self.active_trades)
        
        slots_data = []
        for slot_id, trade in self.active_trades.items():
            slots_data.append({
                "id": slot_id,
                "type": trade.get('wing', 'UNKNOWN'),
                "status": "ACTIVE",
                "asset": trade.get('symbol', 'UNKNOWN'),
                "entry_price": trade.get('entry', 0.0),
                "current_price": 0.0,  # Would need live fetch
                "pnl": 0.0
            })
        
        return {
            "status": "RUNNING" if self.running else "STOPPED",
            "architecture": "VORTEX_V2",
            "scalp_slots": {
                "total": self.scalp_slots,
                "active": sum(1 for t in self.active_trades.values() if t.get('wing') == 'PIRANHA'),
                "idle": self.scalp_slots - sum(1 for t in self.active_trades.values() if t.get('wing') == 'PIRANHA')
            },
            "grid_slots": {
                "total": self.grid_slots,
                "active": sum(1 for t in self.active_trades.values() if t.get('wing') == 'HARVESTER'),
                "idle": self.grid_slots - sum(1 for t in self.active_trades.values() if t.get('wing') == 'HARVESTER')
            },
            "pulse_interval": self.pulse_interval,
            "stake_amount": self.stake_amount,
            "top_movers_count": 0,  # V2 doesn't track this the same way
            "auto_healer": {
                "is_throttled": self.is_throttled,
                "throttle_count": self.throttle_count,
                "current_pulse": f"{self.pulse_interval}s",
                "default_pulse": f"{self.default_pulse_interval}s",
                "throttled_pulse": f"{self.throttled_pulse_interval}s"
            },
            "slots": slots_data
        }

VortexEngine = VortexBerserker