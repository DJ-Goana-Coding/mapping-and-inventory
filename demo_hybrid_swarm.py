#!/usr/bin/env python3
"""
Hybrid Swarm Demo Script
Demonstrates the dual-purpose fleet architecture with visual output
"""

import asyncio
import json
from vortex_restored import VortexBerserker

def print_banner():
    """Display the Hybrid Swarm banner"""
    print("\n" + "=" * 80)
    print("🌊 T.I.A. HYBRID SWARM - DUAL-PURPOSE FLEET DEMO")
    print("=" * 80)
    print("⚡ 4 Piranha Scalp Slots: Quick 0.4% wins (Pay for gas)")
    print("🎯 3 Trailing Grid Slots: Ride the pumps with trailing stops")
    print("=" * 80 + "\n")

async def demo_telemetry():
    """Demonstrate the enhanced telemetry"""
    print("📊 ENHANCED TELEMETRY DEMONSTRATION")
    print("-" * 80)
    
    engine = VortexBerserker()
    
    # Start the engine
    await engine.start()
    
    # Get telemetry
    telemetry = await engine.get_telemetry()
    
    print(f"\n🏗️  Architecture: {telemetry['architecture']}")
    print(f"📡 Status: {telemetry['status']}")
    print(f"⏱️  Pulse Interval: {telemetry['pulse_interval']} seconds")
    print(f"💰 Stake per Slot: ${telemetry['stake_amount']}")
    
    print(f"\n🐟 PIRANHA SCALP SLOTS:")
    print(f"   Total: {telemetry['scalp_slots']['total']}")
    print(f"   Active: {telemetry['scalp_slots']['active']}")
    print(f"   Idle: {telemetry['scalp_slots']['idle']}")
    
    print(f"\n🎯 TRAILING GRID SLOTS:")
    print(f"   Total: {telemetry['grid_slots']['total']}")
    print(f"   Active: {telemetry['grid_slots']['active']}")
    print(f"   Idle: {telemetry['grid_slots']['idle']}")
    
    print("\n📋 INDIVIDUAL SLOT STATUS:")
    print("-" * 80)
    print(f"{'ID':<4} {'Type':<8} {'Status':<8} {'Asset':<15} {'Entry $':<12} {'Current $':<12} {'P&L %':<8}")
    print("-" * 80)
    
    for slot in telemetry['slots']:
        print(f"{slot['id']:<4} {slot['type']:<8} {slot['status']:<8} {slot['asset']:<15} "
              f"{slot['entry_price']:<12.6f} {slot['current_price']:<12.6f} {slot['pnl']:<8.2f}")
    
    await engine.stop()
    print("-" * 80 + "\n")

def demo_slot_types():
    """Show the slot segmentation"""
    print("🎯 SLOT SEGMENTATION")
    print("-" * 80)
    
    engine = VortexBerserker()
    
    print("\n📊 Slot Distribution:")
    print(f"   Slots 1-4: PIRANHA SCALP (Quick 0.4% exits)")
    print(f"   Slots 5-7: TRAILING GRID (Ride the pumps)")
    
    print("\n📋 Detailed Slot Configuration:")
    print("-" * 80)
    print(f"{'Slot ID':<10} {'Type':<15} {'Capital':<12} {'Strategy':<40}")
    print("-" * 80)
    
    for slot in engine.slots:
        strategy = "Exit at +0.4%" if slot.slot_type == "SCALP" else "Trail with 0.5% steps, exit at -1.5% from peak"
        print(f"{slot.id:<10} {slot.slot_type:<15} ${slot.capital:<11.2f} {strategy:<40}")
    
    print("-" * 80 + "\n")

def demo_trading_parameters():
    """Display trading parameters"""
    print("⚙️  TRADING PARAMETERS")
    print("-" * 80)
    
    engine = VortexBerserker()
    
    print("\n🐟 PIRANHA SCALP SETTINGS:")
    print(f"   Take Profit: {engine.scalp_take_profit * 100}% (Hard exit)")
    print(f"   Strategy: Buy top momentum, quick exit")
    print(f"   Goal: ~3.2 cents per win on $8 stake (0.4% gain)")
    
    print("\n🎯 TRAILING GRID SETTINGS:")
    print(f"   Trail Step: {engine.grid_trail_step * 100}% (Move stop up)")
    print(f"   Exit Pullback: {engine.grid_exit_pullback * 100}% (From peak)")
    print(f"   Strategy: Buy spike, trail up, ride the pump")
    print(f"   Goal: Capture explosive moves")
    
    print("\n🎛️  CORE SETTINGS:")
    print(f"   Pulse Interval: {engine.pulse_interval} seconds")
    print(f"   Stake Amount: ${engine.stake_amount} per slot")
    print(f"   Exchange: MEXC")
    print(f"   Market: All USDT pairs")
    print(f"   Total Capital: ${engine.stake_amount * len(engine.slots)} (across {len(engine.slots)} slots)")
    
    print("-" * 80 + "\n")

def demo_architecture_diagram():
    """Display visual architecture diagram"""
    print("🏗️  HYBRID SWARM ARCHITECTURE")
    print("-" * 80)
    print("""
    ┌─────────────────────────────────────────────────────────────────┐
    │                     HYBRID SWARM ENGINE                         │
    │                    (7 Slots, $8 each = $56)                     │
    └─────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
         ┌──────────▼──────────┐      ┌──────────▼──────────┐
         │  PIRANHA SCALP      │      │  TRAILING GRID      │
         │  (4 Slots)          │      │  (3 Slots)          │
         │  IDs: 1, 2, 3, 4    │      │  IDs: 5, 6, 7       │
         └─────────────────────┘      └─────────────────────┘
                    │                             │
         ┌──────────▼──────────┐      ┌──────────▼──────────┐
         │  STRATEGY           │      │  STRATEGY           │
         │  • Top momentum     │      │  • Strongest movers │
         │  • Quick entry      │      │  • Hold & trail     │
         │  • Exit at +0.4%    │      │  • Trail +0.5%      │
         │  • Fast turnover    │      │  • Exit at -1.5%    │
         └─────────────────────┘      └─────────────────────┘
                    │                             │
         ┌──────────▼──────────┐      ┌──────────▼──────────┐
         │  GOAL               │      │  GOAL               │
         │  Pay for "gas"      │      │  Capture big runs   │
         │  Small consistent   │      │  Ride the pumps     │
         │  wins               │      │  Moon bags          │
         └─────────────────────┘      └─────────────────────┘
    """)
    print("-" * 80 + "\n")

async def main():
    """Run the complete demo"""
    print_banner()
    demo_architecture_diagram()
    demo_slot_types()
    demo_trading_parameters()
    await demo_telemetry()
    
    print("=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)
    print("\n🚀 The Hybrid Swarm is ready for deployment:")
    print("   • Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables")
    print("   • Deploy to your Frankfurt node")
    print("   • Watch the two-front war begin!")
    print("\n📡 Monitor via /telemetry endpoint to see:")
    print("   • Which slots are Scalps vs Grids")
    print("   • Active positions and P&L")
    print("   • Performance by slot type")
    print("\n🌊 Commander, the Hybrid Swarm awaits your command!\n")

if __name__ == "__main__":
    asyncio.run(main())
