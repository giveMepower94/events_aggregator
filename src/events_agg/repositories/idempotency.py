from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.models.idempotency import IdempotencyKey


class IdempotencyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_key(self, idempotency_key: str) -> IdempotencyKey | None:
        result = await self.session.execute(
            select(IdempotencyKey).where(IdempotencyKey.idempotency_key == idempotency_key)
        )
        return result.scalars().first()

    async def create_processing(
        self,
        idempotency_key: str,
        request_hash: str,
    ) -> IdempotencyKey:
        record = IdempotencyKey(
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            status="processing",
            ticket_id=None,
            created_at=datetime.now(timezone.utc),
            completed_at=None,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def mark_completed(
        self,
        record: IdempotencyKey,
        ticket_id: str,
    ) -> IdempotencyKey:
        record.status = "completed"
        record.ticket_id = ticket_id
        record.completed_at = datetime.now(timezone.utc)
        await self.session.flush()
        return record

    async def delete(self, record: IdempotencyKey) -> None:
        await self.session.delete(record)
        await self.session.flush()
