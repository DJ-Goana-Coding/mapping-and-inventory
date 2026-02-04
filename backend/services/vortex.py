import asyncio
import ccxt.async_support as ccxt
import os
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
        # Hybrid Swarm: 4 Piranha Scalp + 3 Trailing Grid
        self.scalp_slots = 4
        self.grid_slots = 3
        
        # Initialize slots with types
        self.slots = []
        for i in range(self.scalp_slots):
            self.slots.append(Slot(i + 1, "SCALP"))
        for i in range(self.grid_slots):
            self.slots.append(Slot(self.scalp_slots + i + 1, "GRID"))
        
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
        
        # Trading parameters
        self.scalp_take_profit = 0.004  # 0.4%
        self.grid_trail_step = 0.005    # 0.5%
        self.grid_exit_pullback = 0.015  # 1.5%
        
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

    async def _execute_scalp_logic(self, slot):
        """Piranha Scalp Logic: Quick 0.4% wins"""
        if slot.status == "IDLE":
            # Look for entry opportunity
            if self.top_movers:
                # Distribute scalp slots across top movers to avoid all trading same coin
                scalp_index = (slot.id - 1) % len(self.top_movers)
                candidate = self.top_movers[scalp_index]
                slot.asset = candidate['symbol']
                slot.entry_price = candidate['price']
                slot.current_price = candidate['price']
                slot.take_profit = slot.entry_price * (1 + self.scalp_take_profit)
                slot.status = "ACTIVE"
                slot.entry_time = datetime.now()
                print(f"🐟 Slot {slot.id} [SCALP] ENTRY: {slot.asset} @ ${slot.entry_price:.6f}")
        
        elif slot.status == "ACTIVE":
            # Check exit conditions
            try:
                ticker = await self.exchange.fetch_ticker(slot.asset)
                slot.current_price = ticker['last']
                slot.pnl = ((slot.current_price - slot.entry_price) / slot.entry_price) * 100
                
                # Hard take-profit at 0.4%
                if slot.current_price >= slot.take_profit:
                    profit = ((slot.current_price - slot.entry_price) / slot.entry_price) * slot.capital
                    print(f"✅ Slot {slot.id} [SCALP] EXIT: {slot.asset} @ ${slot.current_price:.6f} | Profit: ${profit:.2f}")
                    self._reset_slot(slot)
                    
            except Exception as e:
                print(f"⚠️ Slot {slot.id} price check failed: {e}")
    
    async def _execute_grid_logic(self, slot):
        """Trailing Grid Logic: Ride the pump with trailing stop"""
        if slot.status == "IDLE":
            # Look for entry opportunity - strongest momentum
            if len(self.top_movers) > 0:
                # Grid slots target the strongest movers, distributed across available pairs
                # Prevent index out of bounds
                grid_index = min((slot.id - self.scalp_slots - 1), len(self.top_movers) - 1)
                candidate = self.top_movers[grid_index]
                slot.asset = candidate['symbol']
                slot.entry_price = candidate['price']
                slot.current_price = candidate['price']
                slot.peak_price = candidate['price']
                slot.stop_loss = slot.entry_price * (1 - self.grid_exit_pullback)
                slot.status = "ACTIVE"
                slot.entry_time = datetime.now()
                print(f"🎯 Slot {slot.id} [GRID] ENTRY: {slot.asset} @ ${slot.entry_price:.6f}")
        
        elif slot.status == "ACTIVE":
            # Update trailing stop
            try:
                ticker = await self.exchange.fetch_ticker(slot.asset)
                slot.current_price = ticker['last']
                slot.pnl = ((slot.current_price - slot.entry_price) / slot.entry_price) * 100
                
                # Update peak and trail stop up
                if slot.current_price > slot.peak_price:
                    # Price moved up - check if we should trail
                    price_increase = (slot.current_price - slot.peak_price) / slot.peak_price
                    
                    if price_increase >= self.grid_trail_step:
                        # Trail up by 0.5%
                        slot.peak_price = slot.current_price
                        slot.stop_loss = slot.peak_price * (1 - self.grid_exit_pullback)
                        print(f"📈 Slot {slot.id} [GRID] TRAILING: {slot.asset} Peak: ${slot.peak_price:.6f} | Stop: ${slot.stop_loss:.6f}")
                
                # Check exit: 1.5% pullback from peak
                if slot.current_price <= slot.stop_loss:
                    profit = ((slot.current_price - slot.entry_price) / slot.entry_price) * slot.capital
                    print(f"🛑 Slot {slot.id} [GRID] EXIT: {slot.asset} @ ${slot.current_price:.6f} | Profit: ${profit:.2f}")
                    self._reset_slot(slot)
                    
            except Exception as e:
                print(f"⚠️ Slot {slot.id} price check failed: {e}")
    
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
        
        # Auto-Healer: Check if we can recover from throttled state
        self._check_throttle_recovery()
        
        # Scan market for opportunities
        await self._scan_market()
        
        pulse_status = f"⚡ {self.pulse_interval}s" if not self.is_throttled else f"🛡️ {self.pulse_interval}s (Throttled)"
        print(f"💓 Hybrid Swarm Pulse - {len(self.slots)} Slots Active | {pulse_status}")
        
        # Execute logic for each slot based on type
        for slot in self.slots:
            if slot.slot_type == "SCALP":
                await self._execute_scalp_logic(slot)
            elif slot.slot_type == "GRID":
                await self._execute_grid_logic(slot)
    
    async def start(self):
        """Start the Hybrid Swarm engine"""
        self.running = True
        print("🌊 T.I.A. HYBRID SWARM IGNITED!")
        print(f"   4 Piranha Scalps + 3 Trailing Grids")
        print(f"   Pulse: {self.pulse_interval}s | Stake: ${self.stake_amount}")
        
    async def stop(self):
        """Stop the engine"""
        self.running = False
        print("🛑 Hybrid Swarm stopped")
        
    async def get_telemetry(self):
        """Enhanced telemetry with slot type tracking"""
        scalp_active = sum(1 for s in self.slots if s.slot_type == "SCALP" and s.status == "ACTIVE")
        grid_active = sum(1 for s in self.slots if s.slot_type == "GRID" and s.status == "ACTIVE")
        
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
            if s.slot_type == "GRID" and s.status == "ACTIVE":
                slot_info["peak_price"] = s.peak_price
                slot_info["stop_loss"] = s.stop_loss
            elif s.slot_type == "SCALP" and s.status == "ACTIVE":
                slot_info["take_profit"] = s.take_profit
                
            slots_data.append(slot_info)
        
        return {
            "status": "RUNNING" if self.running else "STOPPED",
            "architecture": "HYBRID_SWARM",
            "scalp_slots": {
                "total": self.scalp_slots,
                "active": scalp_active,
                "idle": self.scalp_slots - scalp_active
            },
            "grid_slots": {
                "total": self.grid_slots,
                "active": grid_active,
                "idle": self.grid_slots - grid_active
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