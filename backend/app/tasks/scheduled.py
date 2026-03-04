from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.cleanup_service import CleanupService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduled_tasks():
    # Run cleanup every 15 minutes
    scheduler.add_job(
        CleanupService.cleanup_expired_files,
        "interval",
        minutes=15,
        id="cleanup_expired_files",
        name="Clean up expired PDF files",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("scheduled_tasks_started")


def shutdown_scheduled_tasks():
    scheduler.shutdown(wait=False)
    logger.info("scheduled_tasks_stopped")