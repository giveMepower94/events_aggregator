import logging

from src.events_agg.core.config import settings
from src.events_agg.db.session import AsyncSessionLocal
from src.events_agg.repositories.outbox import OutboxRepository

logger = logging.getLogger(__name__)


async def process_outbox_batch() -> None:
    async with AsyncSessionLocal() as session:
        repo = OutboxRepository(session)
        messages = await repo.list_pending(limit=settings.outbox_batch_size)

        if not messages:
            return

        logger.info("Outbox pending messages found: %s", len(messages))
