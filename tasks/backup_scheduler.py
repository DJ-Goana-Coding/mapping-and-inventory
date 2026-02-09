"""
Background task for hourly position backups to Google Drive
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
