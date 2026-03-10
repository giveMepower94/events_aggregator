import logging

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.db.session import AsyncSessionLocal
from src.events_agg.usecases.sync_events import SyncEventsUseCase

logger = logging.getLogger(__name__)


async def run_sync_job() -> None:
    logger.info("Starting scheduled sync job")

    async with AsyncSessionLocal() as session:
        try:
            client = EventsProviderClient()
            usecase = SyncEventsUseCase(session=session, client=client)
            result = await usecase.execute()
            logger.info("Scheduled sync job finished: %s", result)
        except Exception:
            logger.exception("Scheduled sync job failed")
            raise
