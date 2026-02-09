import asyncio
import ccxt.async_support as ccxt
import os
import json
from datetime import datetime

class Slot:
    def __init__(self, id, slot_type):
        self.id = id
        self.slot_type = slot_type  # "SCALP" or "GRID"
        self.capital = 8.00  # $8.00 per slot
        self.status = "IDLE"
        self.asset = "None"
        self.entry_price = 0.0
        self.current_price = 0.0
        self.peak_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0
        self.entry_time = None
        self.pnl = 0.0

class VortexBerserker:
    def __init__(self):
        # ⚡ BERSERKER CONFIGURATION: 2 Piranhas + 4 Harvesters + 1 Sniper
        self.piranha_slots = 2   # Slots 1-2: Fast 0.4% scalps
        self.harvester_slots = 4  # Slots 3-6: Momentum riders
        self.sniper_slot = 1      # Slot 7: High-conviction strikes
        
        # Slot type assignments
        self.PIRANHA_SLOTS = [1, 2]
        self.HARVESTER_SLOTS = [3, 4, 5, 6]
        self.SNIPER_SLOT = [7]
        
        # Initialize 7 slots with correct types
        self.slots = []
        
        # Piranhas: Slots 1-2
        for i in self.PIRANHA_SLOTS:
            self.slots.append(Slot(i, "PIRANHA"))
        
        # Harvesters: Slots 3-6
        for i in self.HARVESTER_SLOTS:
            self.slots.append(Slot(i, "HARVESTER"))
        
        # Sniper: Slot 7
        for i in self.SNIPER_SLOT:
            self.slots.append(Slot(i, "SNIPER"))
        
        # Core settings
        self.running = False
        self.pulse_interval = 2  # 2 seconds (can be adjusted by auto-healer)
        self.default_pulse_interval = 2  # Default pulse interval
        self.throttled_pulse_interval = 4  # Throttled pulse interval
        self.stake_amount = 8.00  # $8.00 per slot
        
        # Auto-Healer settings
        self.is_throttled = False
        self.throttle_count = 0
        self.last_throttle_time = None
        self.throttle_recovery_wait = 60  # Wait 60 seconds before trying to recover
        
        # Exchange configuration - MEXC
        self.exchange = None
        self.api_key = os.getenv("MEXC_API_KEY")
        self.secret = os.getenv("MEXC_SECRET_KEY")
        
        # Trading parameters - BERSERKER CALIBRATION
        self.piranha_take_profit = 0.004      # 0.4% quick wins
        self.harvester_trail_step = 0.005     # 0.5% trail increment
        self.harvester_exit_pullback = 0.015  # 1.5% stop loss from peak
        self.harvester_min_momentum = 2.0     # 2% minimum momentum threshold
        self.sniper_ema_fast = 9              # Fast EMA for crossover
        self.sniper_ema_slow = 21             # Slow EMA for crossover
        self.sniper_min_confidence = 0.85     # 85% confidence threshold
        self.sniper_crossover_threshold = 0.3 # 0.3% minimum EMA separation
        self.sniper_take_profit_pct = 0.015   # 1.5% target
        self.sniper_stop_loss_pct = 0.005     # 0.5% stop
        
        # Market data cache
        self.top_movers = []
        self.last_scan_time = None

    async def _init_exchange(self):
        """Initialize MEXC exchange connection"""
        if not self.exchange and self.api_key:
            try:
                self.exchange = ccxt.mexc({
                    'apiKey': self.api_key,
                    'secret': self.secret,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot'
                    }
                })
                await self.exchange.load_markets()
                print("✅ MEXC Exchange initialized successfully")
            except Exception as e:
                print(f"❌ Exchange initialization failed: {e}")
    
    def _handle_rate_limit_error(self, error):
        """Auto-Healer: Handle rate limiting by adjusting pulse interval"""
        error_str = str(error).lower()
        
        # Check if this is a rate limit error (429 or rate limit message)
        is_rate_limit = ('429' in error_str or 
                        'rate limit' in error_str or 
                        'too many requests' in error_str)
        
        if is_rate_limit and not self.is_throttled:
            self.is_throttled = True
            self.throttle_count += 1
            self.last_throttle_time = datetime.now()
            self.pulse_interval = self.throttled_pulse_interval
            print(f"🛡️ AUTO-HEALER ACTIVATED: Rate limit detected (#{self.throttle_count})")
            print(f"   Pulse interval adjusted: {self.default_pulse_interval}s → {self.throttled_pulse_interval}s")
            return True
        return False
    
    def _check_throttle_recovery(self):
        """Auto-Healer: Check if we can recover from throttled state"""
        if not self.is_throttled:
            return
        
        if self.last_throttle_time:
            time_since_throttle = (datetime.now() - self.last_throttle_time).total_seconds()
            
            if time_since_throttle >= self.throttle_recovery_wait:
                self.is_throttled = False
                self.pulse_interval = self.default_pulse_interval
                print(f"✅ AUTO-HEALER RECOVERY: Perimeter clear")
                print(f"   Pulse interval restored: {self.throttled_pulse_interval}s → {self.default_pulse_interval}s")
    
    async def _scan_market(self):
        """Scan entire USDT market and sort by 1-minute momentum"""
        if not self.exchange:
            return
        
        try:
            # Fetch all tickers for USDT pairs
            tickers = await self.exchange.fetch_tickers()
            
            # Filter for USDT pairs and calculate momentum
            usdt_pairs = []
            for symbol, ticker in tickers.items():
                if '/USDT' in symbol and ticker.get('percentage'):
                    usdt_pairs.append({
                        'symbol': symbol,
                        'momentum': ticker['percentage'],
                        'price': ticker['last'],
                        'volume': ticker.get('quoteVolume', 0)
                    })
            
            # Sort by momentum (descending)
            self.top_movers = sorted(usdt_pairs, key=lambda x: x['momentum'], reverse=True)
            self.last_scan_time = datetime.now()
            
            if self.top_movers:
                print(f"🎯 Market scanned: {len(self.top_movers)} USDT pairs found")
                print(f"   Top 3: {[m['symbol'] for m in self.top_movers[:3]]}")
            
        except Exception as e:
            # Auto-Healer: Check if this is a rate limit error
            if not self._handle_rate_limit_error(e):
                print(f"⚠️ Market scan error: {e}")
            self.top_movers = []

    async def _execute_piranha_logic(self, slot):
        """
        PIRANHA LOGIC: Fast 0.4% scalps on top movers.
        Slots 1-2: Entry on momentum spike, exit at fixed 0.4% profit.
        """
        if slot.status == "IDLE":
            if self.top_movers:
                # Distribute piranhas across top movers
                piranha_index = (slot.id - 1) % min(3, len(self.top_movers))
                candidate = self.top_movers[piranha_index]
                
                slot.asset = candidate['symbol']
                slot.entry_price = candidate['price']
                slot.current_price = candidate['price']
                slot.take_profit = slot.entry_price * (1 + self.piranha_take_profit)
                slot.status = "ACTIVE"
                slot.entry_time = datetime.now()
                print(f"🐟 [T.I.A.] Slot {slot.id} [PIRANHA] ENTRY: {slot.asset} @ ${slot.entry_price:.6f} | Target: ${slot.take_profit:.6f}")
        
        elif slot.status == "ACTIVE":
            try:
                ticker = await self.exchange.fetch_ticker(slot.asset)
                slot.current_price = ticker['last']
                slot.pnl = ((slot.current_price - slot.entry_price) / slot.entry_price) * 100
                
                # Hard take-profit at 0.4%
                if slot.current_price >= slot.take_profit:
                    profit = ((slot.current_price - slot.entry_price) / slot.entry_price) * slot.capital
                    print(f"✅ [T.I.A.] Slot {slot.id} [PIRANHA] EXIT: {slot.asset} @ ${slot.current_price:.6f} | Profit: ${profit:.2f} ({slot.pnl:.2f}%)")
                    await self._log_trade(slot, "EXIT", profit)
                    self._reset_slot(slot)
            except Exception as e:
                print(f"⚠️ [T.I.A.] Slot {slot.id} price check failed: {e}")

    async def _execute_harvester_logic(self, slot):
        """
        HARVESTER LOGIC: Trailing stops on sustained momentum.
        Slots 3-6: Entry on strong momentum, trail stop up with 0.5% increments, exit on 1.5% pullback.
        """
        if slot.status == "IDLE":
            if len(self.top_movers) > 0:
                # Harvesters target top momentum coins
                harvester_index = min((slot.id - 3), len(self.top_movers) - 1)
                candidate = self.top_movers[harvester_index]
                
                # Require minimum momentum threshold
                if candidate['momentum'] < self.harvester_min_momentum:
                    return
                
                slot.asset = candidate['symbol']
                slot.entry_price = candidate['price']
                slot.current_price = candidate['price']
                slot.peak_price = candidate['price']
                slot.stop_loss = slot.entry_price * (1 - self.harvester_exit_pullback)
                slot.status = "ACTIVE"
                slot.entry_time = datetime.now()
                print(f"🌾 [T.I.A.] Slot {slot.id} [HARVESTER] ENTRY: {slot.asset} @ ${slot.entry_price:.6f} | Momentum: {candidate['momentum']:.2f}%")
        
        elif slot.status == "ACTIVE":
            try:
                ticker = await self.exchange.fetch_ticker(slot.asset)
                slot.current_price = ticker['last']
                slot.pnl = ((slot.current_price - slot.entry_price) / slot.entry_price) * 100
                
                # Update peak and trail stop up
                if slot.current_price > slot.peak_price:
                    price_increase = (slot.current_price - slot.peak_price) / slot.peak_price
                    
                    if price_increase >= self.harvester_trail_step:
                        slot.peak_price = slot.current_price
                        slot.stop_loss = slot.peak_price * (1 - self.harvester_exit_pullback)
                        print(f"📈 [T.I.A.] Slot {slot.id} [HARVESTER] TRAILING: {slot.asset} Peak: ${slot.peak_price:.6f} | Stop: ${slot.stop_loss:.6f}")
                
                # Check exit: 1.5% pullback from peak
                if slot.current_price <= slot.stop_loss:
                    profit = ((slot.current_price - slot.entry_price) / slot.entry_price) * slot.capital
                    print(f"🛑 [T.I.A.] Slot {slot.id} [HARVESTER] EXIT: {slot.asset} @ ${slot.current_price:.6f} | Profit: ${profit:.2f} ({slot.pnl:.2f}%)")
                    await self._log_trade(slot, "EXIT", profit)
                    self._reset_slot(slot)
            except Exception as e:
                print(f"⚠️ [T.I.A.] Slot {slot.id} price check failed: {e}")

    async def _execute_sniper_logic(self, slot):
        """
        SNIPER LOGIC: High-conviction EMA crossover strikes.
        Slot 7: Entry ONLY on strong EMA9/21 crossover with 85%+ confidence.
        """
        if slot.status == "IDLE":
            if len(self.top_movers) > 0:
                # Sniper only fires on THE best opportunity
                candidate = self.top_movers[0]
                
                # Fetch historical data for EMA calculation
                try:
                    ohlcv = await self.exchange.fetch_ohlcv(
                        candidate['symbol'], 
                        timeframe='1m', 
                        limit=50
                    )
                    
                    if len(ohlcv) < 21:
                        return  # Not enough data
                    
                    # Calculate EMAs
                    closes = [candle[4] for candle in ohlcv]
                    ema9 = self._calculate_ema(closes, self.sniper_ema_fast)
                    ema21 = self._calculate_ema(closes, self.sniper_ema_slow)
                    
                    # Check for bullish crossover with strong separation
                    crossover_strength = (ema9 - ema21) / ema21 * 100
                    
                    # SNIPER FIRES: EMA9 > EMA21 AND separation > threshold
                    if ema9 > ema21 and crossover_strength > self.sniper_crossover_threshold:
                        confidence = min(0.85 + (crossover_strength * 0.1), 0.99)
                        
                        if confidence >= self.sniper_min_confidence:
                            slot.asset = candidate['symbol']
                            slot.entry_price = candidate['price']
                            slot.current_price = candidate['price']
                            slot.take_profit = slot.entry_price * (1 + self.sniper_take_profit_pct)
                            slot.stop_loss = slot.entry_price * (1 - self.sniper_stop_loss_pct)
                            slot.status = "ACTIVE"
                            slot.entry_time = datetime.now()
                            print(f"🎯 [T.I.A.] Slot {slot.id} [SNIPER] LOCKED: {slot.asset} @ ${slot.entry_price:.6f} | Confidence: {confidence:.2%} | Crossover: {crossover_strength:.2f}%")
                except Exception as e:
                    print(f"⚠️ [T.I.A.] Sniper EMA calculation failed: {e}")
        
        elif slot.status == "ACTIVE":
            try:
                ticker = await self.exchange.fetch_ticker(slot.asset)
                slot.current_price = ticker['last']
                slot.pnl = ((slot.current_price - slot.entry_price) / slot.entry_price) * 100
                
                # Take profit or stop loss
                if slot.current_price >= slot.take_profit:
                    profit = ((slot.current_price - slot.entry_price) / slot.entry_price) * slot.capital
                    print(f"🎯✅ [T.I.A.] Slot {slot.id} [SNIPER] TARGET HIT: {slot.asset} @ ${slot.current_price:.6f} | Profit: ${profit:.2f} ({slot.pnl:.2f}%)")
                    await self._log_trade(slot, "TARGET_HIT", profit)
                    self._reset_slot(slot)
                elif slot.current_price <= slot.stop_loss:
                    profit = ((slot.current_price - slot.entry_price) / slot.entry_price) * slot.capital
                    print(f"🎯🛑 [T.I.A.] Slot {slot.id} [SNIPER] STOPPED OUT: {slot.asset} @ ${slot.current_price:.6f} | Loss: ${profit:.2f} ({slot.pnl:.2f}%)")
                    await self._log_trade(slot, "STOP_LOSS", profit)
                    self._reset_slot(slot)
            except Exception as e:
                print(f"⚠️ [T.I.A.] Slot {slot.id} price check failed: {e}")

    def _calculate_ema(self, data, period):
        """Calculate Exponential Moving Average with proper SMA initialization"""
        if len(data) < period:
            return data[-1]  # Not enough data, return last price
        
        # Start with Simple Moving Average of first 'period' values
        sma = sum(data[:period]) / period
        
        # Apply exponential smoothing to remaining values
        multiplier = 2 / (period + 1)
        ema = sma
        
        for price in data[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _reset_slot(self, slot):
        """Reset slot to IDLE state"""
        slot.status = "IDLE"
        slot.asset = "None"
        slot.entry_price = 0.0
        slot.current_price = 0.0
        slot.peak_price = 0.0
        slot.stop_loss = 0.0
        slot.take_profit = 0.0
        slot.entry_time = None
        slot.pnl = 0.0

    async def heartbeat(self):
        """Main pulse loop - executes every 2 seconds (or 4 if throttled)"""
        if not self.running:
            return
        
        await self._init_exchange()
        self._check_throttle_recovery()
        await self._scan_market()
        
        pulse_status = f"⚡ {self.pulse_interval}s" if not self.is_throttled else f"🛡️ {self.pulse_interval}s (Throttled)"
        print(f"💓 [T.I.A.] Berserker Vortex Pulse - 7 Slots (2P+4H+1S) | {pulse_status}")
        
        # Execute logic for each slot based on type
        for slot in self.slots:
            if slot.slot_type == "PIRANHA":
                await self._execute_piranha_logic(slot)
            elif slot.slot_type == "HARVESTER":
                await self._execute_harvester_logic(slot)
            elif slot.slot_type == "SNIPER":
                await self._execute_sniper_logic(slot)
    
    async def start(self):
        """Start the Hybrid Swarm engine with safety checks"""
        
        # SAFETY CHECK 1: Verify MEXC credentials in LIVE mode
        execution_mode = os.getenv("EXECUTION_MODE", "PAPER")
        
        if execution_mode == "LIVE":
            if not self.api_key or not self.secret:
                print("🚨 [T.I.A.] CRITICAL: LIVE mode requires MEXC_API_KEY and MEXC_SECRET_KEY")
                print("   LOCKING ALL TRADING SLOTS - SET CREDENTIALS OR SWITCH TO PAPER MODE")
                return  # DO NOT START
            
            # Validate API key works
            try:
                await self._init_exchange()
                balance = await self.exchange.fetch_balance()
                print(f"✅ [T.I.A.] MEXC API validated - Balance: {balance.get('USDT', {}).get('free', 0):.2f} USDT")
            except Exception as e:
                print(f"🚨 [T.I.A.] CRITICAL: MEXC API validation failed - {e}")
                print("   LOCKING ALL TRADING SLOTS")
                return
        
        # SAFETY CHECK 2: Stake amount consistency
        expected_stake = 8.00  # Admiral's mandate
        if abs(self.stake_amount - expected_stake) > 0.01:
            print(f"⚠️ [T.I.A.] WARNING: Stake mismatch - Expected ${expected_stake}, Got ${self.stake_amount}")
            print("   Adjusting to Admiral's mandate...")
            self.stake_amount = expected_stake
        
        # SAFETY CHECK 3: Verify 2/4/1 configuration
        total_slots = len(self.slots)
        piranha_count = sum(1 for s in self.slots if s.slot_type == "PIRANHA")
        harvester_count = sum(1 for s in self.slots if s.slot_type == "HARVESTER")
        sniper_count = sum(1 for s in self.slots if s.slot_type == "SNIPER")
        
        if not (total_slots == 7 and piranha_count == 2 and harvester_count == 4 and sniper_count == 1):
            print(f"🚨 [T.I.A.] CRITICAL: Slot configuration mismatch!")
            print(f"   Expected: 2 Piranhas, 4 Harvesters, 1 Sniper")
            print(f"   Got: {piranha_count} Piranhas, {harvester_count} Harvesters, {sniper_count} Sniper")
            print("   LOCKING ALL TRADING SLOTS")
            return
        
        # All checks passed - engage
        self.running = True
        print("🌊 [T.I.A.] BERSERKER VORTEX IGNITED!")
        print(f"   Configuration: 2 Piranhas + 4 Harvesters + 1 Sniper")
        print(f"   Mode: {execution_mode}")
        print(f"   Pulse: {self.pulse_interval}s | Stake: ${self.stake_amount}")
        print(f"   Safety Locks: ENGAGED ✅")
        
    async def stop(self):
        """Stop the engine with emergency state dump"""
        print("🛑 [T.I.A.] Berserker Vortex shutdown initiated...")
        
        # Emergency airgap dump before stopping
        await self._secure_airgap_dump()
        
        self.running = False
        print("✅ [T.I.A.] Shutdown complete - State preserved in airgap")
        
    async def _log_trade(self, slot, action, profit):
        """
        Log trade to shadow archive and Hugging Face for forensic continuity.
        
        Args:
            slot: Slot object
            action: "EXIT", "TARGET_HIT", "STOP_LOSS"
            profit: Profit/loss amount
        """
        trade_log = {
            "timestamp": datetime.now().isoformat(),
            "slot_id": slot.id,
            "slot_type": slot.slot_type,
            "action": action,
            "asset": slot.asset,
            "entry_price": slot.entry_price,
            "exit_price": slot.current_price,
            "pnl_percent": slot.pnl,
            "profit_usd": profit,
            "duration_seconds": (datetime.now() - slot.entry_time).total_seconds() if slot.entry_time else 0
        }
        
        # Write to shadow archive
        await self._push_to_shadow_archive(trade_log)
        
        # Push to Hugging Face (if configured)
        await self._push_to_huggingface(trade_log)
        
        print(f"📝 [T.I.A.] Trade logged - Slot {slot.id} {action}")

    async def _push_to_shadow_archive(self, trade_log):
        """Write trade log to local shadow archive"""
        try:
            shadow_path = os.getenv("SHADOW_ARCHIVE_PATH", "/app/shadow_archive")
            os.makedirs(shadow_path, exist_ok=True)
            
            # Append to daily log file
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(shadow_path, f"trades_{date_str}.jsonl")
            
            # Atomic write
            with open(log_file, "a") as f:
                f.write(json.dumps(trade_log) + "\n")
                f.flush()
                os.fsync(f.fileno())
            
            print(f"✅ [T.I.A.] Shadow archive updated: {log_file}")
        except Exception as e:
            print(f"⚠️ [T.I.A.] Shadow archive write failed: {e}")

    async def _push_to_huggingface(self, trade_log):
        """Push trade log to Hugging Face for cloud backup"""
        try:
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            hf_dataset = os.getenv("HF_TRADE_LOG_DATASET")  # e.g., "DJ-Goana-Coding/trade-logs"
            
            if not hf_token or not hf_dataset:
                return  # HF backup not configured
            
            from huggingface_hub import HfApi
            api = HfApi()
            
            # Upload to dataset
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Create temporary file
            temp_file = f"/tmp/trade_{datetime.now().timestamp()}.json"
            with open(temp_file, "w") as f:
                json.dump(trade_log, f)
            
            # Upload to HF
            api.upload_file(
                path_or_fileobj=temp_file,
                path_in_repo=f"trades/{date_str}/{datetime.now().timestamp()}.json",
                repo_id=hf_dataset,
                repo_type="dataset",
                token=hf_token
            )
            
            os.remove(temp_file)
            print(f"☁️ [T.I.A.] Hugging Face backup complete")
        except Exception as e:
            print(f"⚠️ [T.I.A.] Hugging Face backup failed: {e}")

    async def _secure_airgap_dump(self):
        """
        Emergency dump of all current positions to airgap storage.
        Called before shutdown or on critical error.
        """
        try:
            airgap_path = os.getenv("AIRGAP_PATH", "/app/airgap")
            os.makedirs(airgap_path, exist_ok=True)
            
            # Dump current state
            state = {
                "timestamp": datetime.now().isoformat(),
                "running": self.running,
                "wallet_balance": getattr(self, 'wallet_balance', 0),
                "total_profit": getattr(self, 'total_profit', 0),
                "slots": []
            }
            
            for slot in self.slots:
                state["slots"].append({
                    "id": slot.id,
                    "type": slot.slot_type,
                    "status": slot.status,
                    "asset": slot.asset,
                    "entry_price": slot.entry_price,
                    "current_price": slot.current_price,
                    "pnl": slot.pnl
                })
            
            # Atomic write
            dump_file = os.path.join(airgap_path, "emergency_dump.json")
            temp_file = dump_file + ".tmp"
            
            with open(temp_file, "w") as f:
                json.dump(state, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            os.rename(temp_file, dump_file)
            print(f"🛡️ [T.I.A.] Airgap dump complete: {dump_file}")
        except Exception as e:
            print(f"🚨 [T.I.A.] CRITICAL: Airgap dump failed - {e}")
        
    async def get_telemetry(self):
        """Enhanced telemetry with slot type tracking"""
        piranha_active = sum(1 for s in self.slots if s.slot_type == "PIRANHA" and s.status == "ACTIVE")
        harvester_active = sum(1 for s in self.slots if s.slot_type == "HARVESTER" and s.status == "ACTIVE")
        sniper_active = sum(1 for s in self.slots if s.slot_type == "SNIPER" and s.status == "ACTIVE")
        
        slots_data = []
        for s in self.slots:
            slot_info = {
                "id": s.id,
                "type": s.slot_type,
                "status": s.status,
                "asset": s.asset,
                "entry_price": s.entry_price,
                "current_price": s.current_price,
                "pnl": round(s.pnl, 2) if s.status == "ACTIVE" else 0.0
            }
            
            # Add type-specific data
            if s.slot_type == "HARVESTER" and s.status == "ACTIVE":
                slot_info["peak_price"] = s.peak_price
                slot_info["stop_loss"] = s.stop_loss
            elif s.slot_type == "PIRANHA" and s.status == "ACTIVE":
                slot_info["take_profit"] = s.take_profit
            elif s.slot_type == "SNIPER" and s.status == "ACTIVE":
                slot_info["take_profit"] = s.take_profit
                slot_info["stop_loss"] = s.stop_loss
                
            slots_data.append(slot_info)
        
        return {
            "status": "RUNNING" if self.running else "STOPPED",
            "architecture": "BERSERKER_VORTEX",
            "piranha_slots": {
                "total": self.piranha_slots,
                "active": piranha_active,
                "idle": self.piranha_slots - piranha_active
            },
            "harvester_slots": {
                "total": self.harvester_slots,
                "active": harvester_active,
                "idle": self.harvester_slots - harvester_active
            },
            "sniper_slot": {
                "total": self.sniper_slot,
                "active": sniper_active,
                "idle": self.sniper_slot - sniper_active
            },
            "pulse_interval": self.pulse_interval,
            "stake_amount": self.stake_amount,
            "top_movers_count": len(self.top_movers),
            "auto_healer": {
                "is_throttled": self.is_throttled,
                "throttle_count": self.throttle_count,
                "current_pulse": f"{self.pulse_interval}s",
                "default_pulse": f"{self.default_pulse_interval}s",
                "throttled_pulse": f"{self.throttled_pulse_interval}s"
            },
            "slots": slots_data
        }

# Backward compatibility alias for legacy imports
# VortexEngine has been renamed to VortexBerserker for the hardened implementation
# This alias ensures existing code continues to work without breaking changes
VortexEngine = VortexBerserker