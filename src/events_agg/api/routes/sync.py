from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.db.session import get_session
from src.events_agg.usecases.sync_events import SyncEventsUseCase


router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/trigger")
async def trigger_sync(
    session: AsyncSession = Depends(get_session)
) -> dict[str, int | str]:
    client = EventsProviderClient()
    usecase = SyncEventsUseCase(session=session, client=client)
    return await usecase.execute()
