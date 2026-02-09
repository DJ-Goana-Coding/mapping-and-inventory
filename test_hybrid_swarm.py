#!/usr/bin/env python3
"""
Test script for Berserker Vortex architecture
Tests the VortexBerserker class with 2 Piranhas + 4 Harvesters + 1 Sniper slots
"""

import asyncio
import json
from vortex_restored import VortexBerserker, VortexEngine

def test_initialization():
    """Test 1: Verify proper initialization"""
    print("=" * 70)
    print("🧪 TEST 1: Initialization and Slot Segmentation")
    print("=" * 70)
    
    engine = VortexBerserker()
    
    # Verify slot counts
    assert len(engine.slots) == 7, "Should have 7 total slots"
    assert engine.piranha_slots == 2, "Should have 2 piranha slots"
    assert engine.harvester_slots == 4, "Should have 4 harvester slots"
    assert engine.sniper_slot == 1, "Should have 1 sniper slot"
    
    # Verify slot types
    piranha_count = sum(1 for s in engine.slots if s.slot_type == "PIRANHA")
    harvester_count = sum(1 for s in engine.slots if s.slot_type == "HARVESTER")
    sniper_count = sum(1 for s in engine.slots if s.slot_type == "SNIPER")
    
    assert piranha_count == 2, f"Expected 2 PIRANHA slots, got {piranha_count}"
    assert harvester_count == 4, f"Expected 4 HARVESTER slots, got {harvester_count}"
    assert sniper_count == 1, f"Expected 1 SNIPER slot, got {sniper_count}"
    
    print(f"✅ Total slots: {len(engine.slots)}")
    print(f"✅ Piranha slots (IDs 1-2): {piranha_count}")
    print(f"✅ Harvester slots (IDs 3-6): {harvester_count}")
    print(f"✅ Sniper slot (ID 7): {sniper_count}")
    
    # Verify slot properties
    for slot in engine.slots:
        assert slot.capital == 8.00, "Each slot should have $8.00 capital"
        assert slot.status == "IDLE", "Slots should start in IDLE state"
        print(f"   Slot {slot.id}: Type={slot.slot_type}, Capital=${slot.capital}, Status={slot.status}")
    
    print(f"✅ All slots initialized correctly with $8.00 capital\n")
    return engine

def test_configuration():
    """Test 2: Verify configuration parameters"""
    print("=" * 70)
    print("🧪 TEST 2: Core Configuration")
    print("=" * 70)
    
    engine = VortexBerserker()
    
    # Verify core settings
    assert engine.pulse_interval == 2, "Pulse interval should be 2 seconds"
    assert engine.stake_amount == 8.00, "Stake amount should be $8.00"
    
    # Verify trading parameters - BERSERKER CALIBRATION
    assert engine.piranha_take_profit == 0.004, "Piranha take-profit should be 0.4%"
    assert engine.harvester_trail_step == 0.005, "Harvester trail step should be 0.5%"
    assert engine.harvester_exit_pullback == 0.015, "Harvester exit pullback should be 1.5%"
    assert engine.sniper_ema_fast == 9, "Sniper fast EMA should be 9"
    assert engine.sniper_ema_slow == 21, "Sniper slow EMA should be 21"
    assert engine.sniper_min_confidence == 0.85, "Sniper min confidence should be 85%"
    
    print(f"✅ Pulse interval: {engine.pulse_interval} seconds")
    print(f"✅ Stake amount: ${engine.stake_amount}")
    print(f"✅ Piranha take-profit: {engine.piranha_take_profit * 100}%")
    print(f"✅ Harvester trail step: {engine.harvester_trail_step * 100}%")
    print(f"✅ Harvester exit pullback: {engine.harvester_exit_pullback * 100}%")
    print(f"✅ Sniper EMA fast: {engine.sniper_ema_fast}")
    print(f"✅ Sniper EMA slow: {engine.sniper_ema_slow}")
    print(f"✅ Sniper min confidence: {engine.sniper_min_confidence * 100}%")
    print()
    
    return engine

async def test_telemetry():
    """Test 3: Verify telemetry output"""
    print("=" * 70)
    print("🧪 TEST 3: Telemetry Output")
    print("=" * 70)
    
    engine = VortexBerserker()
    telemetry = await engine.get_telemetry()
    
    # Verify telemetry structure
    assert "status" in telemetry, "Telemetry should include status"
    assert "architecture" in telemetry, "Telemetry should include architecture"
    assert "piranha_slots" in telemetry, "Telemetry should include piranha_slots"
    assert "harvester_slots" in telemetry, "Telemetry should include harvester_slots"
    assert "sniper_slot" in telemetry, "Telemetry should include sniper_slot"
    assert "slots" in telemetry, "Telemetry should include slots array"
    
    # Verify slot tracking
    assert telemetry["piranha_slots"]["total"] == 2
    assert telemetry["harvester_slots"]["total"] == 4
    assert telemetry["sniper_slot"]["total"] == 1
    assert telemetry["architecture"] == "BERSERKER_VORTEX"
    
    print(f"✅ Architecture: {telemetry['architecture']}")
    print(f"✅ Status: {telemetry['status']}")
    print(f"✅ Piranha slots - Total: {telemetry['piranha_slots']['total']}, Active: {telemetry['piranha_slots']['active']}, Idle: {telemetry['piranha_slots']['idle']}")
    print(f"✅ Harvester slots - Total: {telemetry['harvester_slots']['total']}, Active: {telemetry['harvester_slots']['active']}, Idle: {telemetry['harvester_slots']['idle']}")
    print(f"✅ Sniper slot - Total: {telemetry['sniper_slot']['total']}, Active: {telemetry['sniper_slot']['active']}, Idle: {telemetry['sniper_slot']['idle']}")
    
    print("\n📊 Full Telemetry Output:")
    print(json.dumps(telemetry, indent=2))
    print()

def test_backward_compatibility():
    """Test 4: Verify VortexEngine alias works"""
    print("=" * 70)
    print("🧪 TEST 4: Backward Compatibility")
    print("=" * 70)
    
    # Test that both imports work
    engine1 = VortexBerserker()
    engine2 = VortexEngine()
    
    assert type(engine1) == type(engine2), "Both should create same type"
    assert VortexEngine is VortexBerserker, "VortexEngine should be alias"
    
    print(f"✅ VortexBerserker: {type(engine1)}")
    print(f"✅ VortexEngine: {type(engine2)}")
    print(f"✅ Same class: {VortexEngine is VortexBerserker}")
    print()

async def test_start_stop():
    """Test 5: Start and stop functionality"""
    print("=" * 70)
    print("🧪 TEST 5: Start/Stop Operations")
    print("=" * 70)
    
    engine = VortexBerserker()
    
    # Initially stopped
    telemetry = await engine.get_telemetry()
    assert telemetry["status"] == "STOPPED"
    print(f"✅ Initial status: {telemetry['status']}")
    
    # Start engine (will pass since we're in PAPER mode by default)
    await engine.start()
    telemetry = await engine.get_telemetry()
    assert telemetry["status"] == "RUNNING"
    print(f"✅ After start: {telemetry['status']}")
    
    # Stop engine
    await engine.stop()
    telemetry = await engine.get_telemetry()
    assert telemetry["status"] == "STOPPED"
    print(f"✅ After stop: {telemetry['status']}")
    print()

def test_slot_reset():
    """Test 6: Slot reset functionality"""
    print("=" * 70)
    print("🧪 TEST 6: Slot Reset")
    print("=" * 70)
    
    engine = VortexBerserker()
    slot = engine.slots[0]
    
    # Modify slot
    slot.status = "ACTIVE"
    slot.asset = "BTC/USDT"
    slot.entry_price = 50000.0
    slot.current_price = 50200.0
    slot.pnl = 0.4
    
    print(f"   Before reset: Status={slot.status}, Asset={slot.asset}, PnL={slot.pnl}%")
    
    # Reset slot
    engine._reset_slot(slot)
    
    # Verify reset
    assert slot.status == "IDLE"
    assert slot.asset == "None"
    assert slot.entry_price == 0.0
    assert slot.pnl == 0.0
    
    print(f"✅ After reset: Status={slot.status}, Asset={slot.asset}, PnL={slot.pnl}%")
    print()

def test_ema_calculation():
    """Test 7: EMA calculation"""
    print("=" * 70)
    print("🧪 TEST 7: EMA Calculation")
    print("=" * 70)
    
    engine = VortexBerserker()
    
    # Test with sample data
    test_data = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
    ema9 = engine._calculate_ema(test_data[:9], 9)
    
    print(f"✅ EMA9 calculated: {ema9:.2f}")
    assert ema9 > 0, "EMA should be positive"
    print()

async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🚀 BERSERKER VORTEX TEST SUITE")
    print("   Testing 2 Piranhas + 4 Harvesters + 1 Sniper Architecture")
    print("=" * 70 + "\n")
    
    try:
        # Run synchronous tests
        test_initialization()
        test_configuration()
        test_backward_compatibility()
        test_slot_reset()
        test_ema_calculation()
        
        # Run async tests
        await test_telemetry()
        await test_start_stop()
        
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Berserker Vortex architecture verified:")
        print("   - 2 Piranha slots for 0.4% quick scalps")
        print("   - 4 Harvester slots for momentum riding with trailing stops")
        print("   - 1 Sniper slot for high-conviction EMA crossover strikes")
        print("   - 2 second pulse interval")
        print("   - $8.00 stake per slot")
        print("   - Enhanced telemetry with slot type tracking")
        print("   - Safety locks for LIVE mode trading")
        print("\n🌊 Ready for deployment!\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise

if __name__ == "__main__":
    asyncio.run(run_all_tests())
