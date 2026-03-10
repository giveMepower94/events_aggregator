import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.events_agg.core.config import settings
from src.events_agg.usecases.run_sync_job import run_sync_job

logger = logging.getLogger(__name__)


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        run_sync_job,
        trigger=CronTrigger(hour=settings.sync_hour, minute=settings.sync_minute),
        id="daily_events_sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    return scheduler
