import logging
import httpx

from src.events_agg.clients.capashino import CapashinoClient
from src.events_agg.core.config import settings
from src.events_agg.db.session import AsyncSessionLocal
from src.events_agg.repositories.outbox import OutboxRepository

logger = logging.getLogger(__name__)


async def process_outbox_batch() -> None:
    async with AsyncSessionLocal() as session:
        repo = OutboxRepository(session)
        client = CapashinoClient()
        messages = await repo.list_pending(limit=settings.outbox_batch_size)

        if not messages:
            return

        logger.info("Outbox pending messages found: %s", len(messages))

        for outbox_message in messages:
            if outbox_message.attempts >= settings.outbox_max_attempts:
                logger.warning(
                    "Outbox message %s skipped: max attempts reached",
                    outbox_message.id,
                )
                continue

            payload = outbox_message.payload

            try:
                if outbox_message.event_type != "ticket_purchased":
                    await repo.mark_failed(
                        outbox_message,
                        f"Unsupported event_type: {outbox_message.event_type}",
                    )
                    await session.commit()
                    continue
                await client.create_notification(
                    message=payload["message"],
                    reference_id=payload["ticket_id"],
                    idempotency_key=f"outbox:{outbox_message.id}",
                )
                await repo.mark_sent(outbox_message)
                await session.commit()

                logger.info(
                    "Outbox message %s processed successfully",
                    outbox_message.id,
                )
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code

                # 5xx — временная ошибка, оставляем pending и повторим позже
                if status_code >= 500:
                    await repo.mark_failed(
                        outbox_message,
                        f"Capashino 5xx error: {status_code}",
                    )
                    await session.commit()
                    logger.warning(
                        "Outbox message %s failed with retryable error %s",
                        outbox_message.id,
                        status_code,
                    )
                    continue
                # 4xx — обычно ошибка данных/авторизации, но запись всё равно не теряем
                await repo.mark_failed(
                    outbox_message,
                    f"Capashino 4xx error: {status_code} {exc.response.text}",
                )
                await session.commit()
                logger.error(
                    "Outbox message %s failed with non-retryable HTTP error %s",
                    outbox_message.id,
                    status_code,
                )

            except Exception as exc:
                await repo.mark_failed(outbox_message, str(exc))
                await session.commit()
                logger.exception(
                    "Outbox message %s processing failed",
                    outbox_message.id,
                )
