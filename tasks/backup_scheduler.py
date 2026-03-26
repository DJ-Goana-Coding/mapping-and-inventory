"""
Background task for hourly position backups to Google Drive and 12-hour
DeepClean maintenance cycles across all primary spokes.
"""
from typing import Dict, List, Optional, Tuple, Any, Union
import asyncio
import logging
from bridge_protocol import backup_active_positions

logger = logging.getLogger(__name__)

async def hourly_backup_task(get_positions_callback):
    """
    Run hourly backup of active positions to Drive.
    
    Args:
        get_positions_callback: Function that returns current active positions
    """
    while True:
        try:
            # Perform backup immediately on start, then every hour
            positions = get_positions_callback()
            backup_active_positions(positions)
            
            await asyncio.sleep(3600)  # 1 hour
            
        except Exception as e:
            logger.error(f"Error in hourly backup task: {e}")


async def medic_scheduler_task(
    targets: Optional[List[str]] = None,
    interval_s: int = 12 * 60 * 60,
) -> None:
    """
    Run the Medic DeepClean protocol on a 12-hour recurring schedule across
    all 4 primary spokes (S10_Phalanx, Oppo_Omega, CGAL_Core, Pioneer).

    Args:
        targets: Directories to sweep.  When None, resolved from the
                 ``MEDIC_TARGETS`` environment variable.
        interval_s: Seconds between clean cycles (default: 43200 = 12 hours).
    """
    from agents.medic import schedule_deep_clean

    logger.info(
        "Medic scheduler task starting — interval=%ds (%.1f hours).",
        interval_s,
        interval_s / 3600,
    )
    await schedule_deep_clean(targets=targets, interval_s=interval_s)
