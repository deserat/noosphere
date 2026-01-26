"""Background job scheduler service using APScheduler.

This module provides background job scheduling for surfacing and cleanup tasks.
Uses AsyncIOScheduler for compatibility with FastAPI's async event loop.
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_config

logger = logging.getLogger(__name__)

# Module-level scheduler instance
scheduler = AsyncIOScheduler()


async def surfacing_job() -> None:
    """Surfacing job placeholder.

    This job will be implemented in Phase 3 to handle spaced repetition surfacing logic.
    Currently logs execution to demonstrate the scheduler is working.
    """
    logger.info("Surfacing job executed (placeholder)")
    # TODO: Implement surfacing logic in Phase 3
    # - Query items due for surfacing
    # - Update surfacing timestamps
    # - Trigger notifications if needed


async def cleanup_job() -> None:
    """Cleanup job placeholder.

    This job will be implemented to handle periodic cleanup tasks.
    Currently logs execution to demonstrate the scheduler is working.
    """
    logger.info("Cleanup job executed (placeholder)")
    # TODO: Implement cleanup logic
    # - Clean up old audit logs
    # - Archive completed conversations
    # - Vacuum database if needed


def start_scheduler() -> None:
    """Start the background scheduler with configured jobs.

    Reads configuration and schedules jobs based on config values.
    Raises exception if scheduler fails to start (fail fast).

    Raises:
        RuntimeError: If scheduler fails to start
        ValueError: If configuration is invalid
    """
    try:
        config = get_config()
        scheduler_config = config.scheduler

        # Check if scheduler is enabled
        if not scheduler_config.get("enabled", True):
            logger.info("Scheduler disabled in configuration, skipping initialization")
            return

        # Get configuration values
        surfacing_interval = scheduler_config.get("surfacing_interval_seconds", 86400)
        batch_size = scheduler_config.get("batch_size", 50)

        logger.info(
            f"Initializing scheduler with surfacing interval: {surfacing_interval}s, "
            f"batch size: {batch_size}"
        )

        # Schedule surfacing job (interval trigger)
        scheduler.add_job(
            surfacing_job,
            "interval",
            seconds=surfacing_interval,
            id="surfacing_job",
            name="Surfacing Job",
            replace_existing=True,
        )
        logger.info(f"Scheduled surfacing job (every {surfacing_interval} seconds)")

        # Schedule cleanup job (cron trigger - daily at 2 AM)
        scheduler.add_job(
            cleanup_job,
            "cron",
            hour=2,
            minute=0,
            id="cleanup_job",
            name="Cleanup Job",
            replace_existing=True,
        )
        logger.info("Scheduled cleanup job (daily at 2:00 AM)")

        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started successfully")

    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise RuntimeError(f"Scheduler initialization failed: {e}") from e


def stop_scheduler() -> None:
    """Stop the background scheduler gracefully.

    Waits for currently executing jobs to complete before shutting down.
    Safe to call even if scheduler is not running.
    """
    try:
        if scheduler.running:
            logger.info("Stopping scheduler...")
            scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped successfully")
        else:
            logger.debug("Scheduler was not running")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        # Don't raise - shutdown errors shouldn't crash the application


def get_scheduler_status() -> str:
    """Get the current status of the scheduler.

    Returns:
        Status string: "running", "stopped", or "not_initialized"
    """
    if scheduler.running:
        return "running"
    elif scheduler.state == 0:  # STATE_STOPPED
        return "stopped"
    else:
        return "not_initialized"
