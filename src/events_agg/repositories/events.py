from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.events_agg.models.event import Event


class EventsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, event_id: int) -> Event | None:
        stmt = (
            select(Event)
            .options(selectinload(Event.place))
            .where(Event.id == event_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        date_from: datetime | None = None
    ) -> tuple[list[Event], int]:

        stmt = (select(Event).options(selectinload(Event.place)))

        count_stmt = select(func.count()).select_from(Event)

        if date_from is not None:
            stmt = stmt.where(func.date(Event.event_time) >= date_from)
            count_stmt = count_stmt.where(
                func.date(Event.event_time) >= date_from
            )

        stmt = (
            stmt.order_by(Event.event_time.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        items_result = await self.session.execute(stmt)
        count_result = await self.session.execute(count_stmt)

        items = list(items_result.scalars().all())
        total = count_result.scalar_one()

        return items, total
