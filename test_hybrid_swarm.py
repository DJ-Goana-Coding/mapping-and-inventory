#!/usr/bin/env python3
"""
Test script for Hybrid Swarm architecture
Tests the VortexBerserker class with 4 Piranha Scalp + 3 Trailing Grid slots
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
    assert engine.scalp_slots == 4, "Should have 4 scalp slots"
    assert engine.grid_slots == 3, "Should have 3 grid slots"
    
    # Verify slot types
    scalp_count = sum(1 for s in engine.slots if s.slot_type == "SCALP")
    grid_count = sum(1 for s in engine.slots if s.slot_type == "GRID")
    
    assert scalp_count == 4, f"Expected 4 SCALP slots, got {scalp_count}"
    assert grid_count == 3, f"Expected 3 GRID slots, got {grid_count}"
    
    print(f"✅ Total slots: {len(engine.slots)}")
    print(f"✅ Scalp slots (IDs 1-4): {scalp_count}")
    print(f"✅ Grid slots (IDs 5-7): {grid_count}")
    
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
    
    # Verify trading parameters
    assert engine.scalp_take_profit == 0.004, "Scalp take-profit should be 0.4%"
    assert engine.grid_trail_step == 0.005, "Grid trail step should be 0.5%"
    assert engine.grid_exit_pullback == 0.015, "Grid exit pullback should be 1.5%"
    
    print(f"✅ Pulse interval: {engine.pulse_interval} seconds")
    print(f"✅ Stake amount: ${engine.stake_amount}")
    print(f"✅ Scalp take-profit: {engine.scalp_take_profit * 100}%")
    print(f"✅ Grid trail step: {engine.grid_trail_step * 100}%")
    print(f"✅ Grid exit pullback: {engine.grid_exit_pullback * 100}%")
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
    assert "scalp_slots" in telemetry, "Telemetry should include scalp_slots"
    assert "grid_slots" in telemetry, "Telemetry should include grid_slots"
    assert "slots" in telemetry, "Telemetry should include slots array"
    
    # Verify slot tracking
    assert telemetry["scalp_slots"]["total"] == 4
    assert telemetry["grid_slots"]["total"] == 3
    assert telemetry["architecture"] == "HYBRID_SWARM"
    
    print(f"✅ Architecture: {telemetry['architecture']}")
    print(f"✅ Status: {telemetry['status']}")
    print(f"✅ Scalp slots - Total: {telemetry['scalp_slots']['total']}, Active: {telemetry['scalp_slots']['active']}, Idle: {telemetry['scalp_slots']['idle']}")
    print(f"✅ Grid slots - Total: {telemetry['grid_slots']['total']}, Active: {telemetry['grid_slots']['active']}, Idle: {telemetry['grid_slots']['idle']}")
    
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
    
    # Start engine
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

async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🚀 HYBRID SWARM TEST SUITE")
    print("   Testing 4 Piranha Scalp + 3 Trailing Grid Architecture")
    print("=" * 70 + "\n")
    
    try:
        # Run synchronous tests
        test_initialization()
        test_configuration()
        test_backward_compatibility()
        test_slot_reset()
        
        # Run async tests
        await test_telemetry()
        await test_start_stop()
        
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Hybrid Swarm architecture verified:")
        print("   - 4 Piranha Scalp slots for 0.4% quick wins")
        print("   - 3 Trailing Grid slots for larger moves")
        print("   - 2 second pulse interval")
        print("   - $8.00 stake per slot")
        print("   - Enhanced telemetry with slot type tracking")
        print("\n🌊 Ready for deployment!\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise

if __name__ == "__main__":
    asyncio.run(run_all_tests())
