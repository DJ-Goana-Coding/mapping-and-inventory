"""
FastAPI Backend for VortexBerserker Hybrid Swarm Trading Engine
Integrates the 4 Piranha Scalp + 3 Trailing Grid slots with Auto-Healer
"""
from typing import Dict, List, Optional, Tuple, Any, Union
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from backend.services.vortex import VortexBerserker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("main")

# Global reference to the trading engine
vortex_engine: VortexBerserker = None
heartbeat_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Initializes and starts the VortexBerserker engine on startup.
    """
    global vortex_engine, heartbeat_task
    
    try:
        # Initialize the VortexBerserker engine
        logger.info("🏰 CITADEL: VortexBerserker Engine Engaged")
        vortex_engine = VortexBerserker()
        
        # Check for required environment variables
        if not vortex_engine.api_key or not vortex_engine.secret:
            logger.warning("⚠️  MEXC API credentials not configured!")
            logger.warning("   Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables")
            logger.warning("   Trading will be disabled until credentials are provided")
        else:
            logger.info("✅ MEXC API credentials found")
        
        # Start the trading engine
        await vortex_engine.start()
        
        # Start the heartbeat loop in background
        async def heartbeat_loop():
            while vortex_engine.running:
                try:
                    await vortex_engine.heartbeat()
                    await asyncio.sleep(vortex_engine.pulse_interval)
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                    await asyncio.sleep(vortex_engine.pulse_interval)
        
        heartbeat_task = asyncio.create_task(heartbeat_loop())
        logger.info("🌊 Hybrid Swarm heartbeat initiated")
        
        yield
        
    finally:
        # Cleanup on shutdown
        if vortex_engine:
            await vortex_engine.stop()
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 VortexBerserker engine shutdown complete")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="VortexBerserker Hybrid Swarm",
    description="4 Piranha Scalp + 3 Trailing Grid slots with Auto-Healer protection",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """
    Root endpoint - provides basic system status
    """
    if not vortex_engine:
        return JSONResponse(
            status_code=503,
            content={"status": "initializing", "message": "Trading engine starting up..."}
        )
    
    return {
        "status": "RUNNING" if vortex_engine.running else "STOPPED",
        "architecture": "HYBRID_SWARM",
        "message": "VortexBerserker Hybrid Swarm - 4 Piranha Scalp + 3 Trailing Grid",
        "version": "1.0.0",
        "endpoints": {
            "/": "System status",
            "/telemetry": "Real-time trading telemetry",
            "/health": "Health check",
            "/start": "Start trading engine (POST)",
            "/stop": "Stop trading engine (POST)"
        }
    }


@app.head("/")
async def root_head():
    """
    HEAD request handler for health checks.
    Returns 200 OK with no body (HEAD requests should only include headers).
    """
    return Response(status_code=200)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    if not vortex_engine:
        return JSONResponse(
            status_code=503,
            content={"healthy": False, "status": "engine_not_initialized"}
        )
    
    return {
        "healthy": True,
        "status": "RUNNING" if vortex_engine.running else "STOPPED",
        "uptime": "operational"
    }


@app.get("/telemetry")
async def get_telemetry():
    """
    Get real-time telemetry data from the trading engine.
    Includes slot status, P&L, auto-healer metrics, etc.
    """
    if not vortex_engine:
        return JSONResponse(
            status_code=503,
            content={"error": "Trading engine not initialized"}
        )
    
    try:
        telemetry = await vortex_engine.get_telemetry()
        return telemetry
    except Exception as e:
        logger.error(f"Error fetching telemetry: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch telemetry: {str(e)}"}
        )


@app.post("/start")
async def start_trading():
    """
    Start the trading engine
    """
    if not vortex_engine:
        return JSONResponse(
            status_code=503,
            content={"error": "Trading engine not initialized"}
        )
    
    if vortex_engine.running:
        return {"status": "already_running", "message": "Trading engine is already active"}
    
    await vortex_engine.start()
    return {"status": "started", "message": "Trading engine activated"}


@app.post("/stop")
async def stop_trading():
    """
    Stop the trading engine
    """
    if not vortex_engine:
        return JSONResponse(
            status_code=503,
            content={"error": "Trading engine not initialized"}
        )
    
    if not vortex_engine.running:
        return {"status": "already_stopped", "message": "Trading engine is already inactive"}
    
    await vortex_engine.stop()
    return {"status": "stopped", "message": "Trading engine deactivated"}


@app.get("/status")
async def get_status():
    """
    Get detailed engine status including configuration
    """
    if not vortex_engine:
        return JSONResponse(
            status_code=503,
            content={"error": "Trading engine not initialized"}
        )
    
    return {
        "running": vortex_engine.running,
        "architecture": "HYBRID_SWARM",
        "configuration": {
            "scalp_slots": vortex_engine.scalp_slots,
            "grid_slots": vortex_engine.grid_slots,
            "total_slots": len(vortex_engine.slots),
            "stake_per_slot": vortex_engine.stake_amount,
            "total_capital": vortex_engine.stake_amount * len(vortex_engine.slots),
            "pulse_interval": vortex_engine.pulse_interval,
            "scalp_take_profit": f"{vortex_engine.scalp_take_profit * 100}%",
            "grid_trail_step": f"{vortex_engine.grid_trail_step * 100}%",
            "grid_exit_pullback": f"{vortex_engine.grid_exit_pullback * 100}%"
        },
        "auto_healer": {
            "is_throttled": vortex_engine.is_throttled,
            "throttle_count": vortex_engine.throttle_count,
            "default_pulse": f"{vortex_engine.default_pulse_interval}s",
            "throttled_pulse": f"{vortex_engine.throttled_pulse_interval}s",
            "recovery_wait": f"{vortex_engine.throttle_recovery_wait}s"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
