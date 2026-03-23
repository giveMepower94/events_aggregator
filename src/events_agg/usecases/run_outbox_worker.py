import asyncio
import logging

from src.events_agg.core.config import settings
from src.events_agg.usecases.process_outbox_batch import process_outbox_batch

logger = logging.getLogger(__name__)


async def run_outbox_worker(stop_event: asyncio.Event) -> None:
    logger.info("Outbox worker started")

    while not stop_event.is_set():
        try:
            await process_outbox_batch()
        except Exception:
            logger.exception("Outbox worker iteration failed")

        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=settings.outbox_poll_interval_seconds,
            )
        except asyncio.TimeoutError:
            continue

    logger.info("Outbox worker stopped")
