from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.api.dependencies import get_events_provider_client
from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.db.session import get_session
from src.events_agg.repositories.events import EventsRepository
from src.events_agg.repositories.idempotency import IdempotencyRepository
from src.events_agg.repositories.outbox import OutboxRepository
from src.events_agg.repositories.tickets import TicketsRepository
from src.events_agg.schemas.tickets import (
    CancelTicketResponseSchema,
    CreateTicketRequestSchema,
    CreateTicketResponseSchema,
)
from src.events_agg.usecases.cancel_ticket import CancelTicketUseCase
from src.events_agg.usecases.create_ticket import CreateTicketUseCase


router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post(
    "",
    response_model=CreateTicketResponseSchema,
    status_code=201,
    responses={
        400: {"description": "Invalid request"},
        404: {"description": "Event not found"},
        409: {"description": "Idempotency conflict"},
        502: {"description": "Events Provider error"},
    },
)
async def create_ticket(
    data: CreateTicketRequestSchema,
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(get_events_provider_client),
) -> CreateTicketResponseSchema:
    usecase = CreateTicketUseCase(
        session=session,
        events=EventsRepository(session),
        tickets=TicketsRepository(session),
        idempotency=IdempotencyRepository(session),
        outbox=OutboxRepository(session),
        client=client,
    )
    return await usecase.execute(data)


@router.delete("/{ticket_id}", response_model=CancelTicketResponseSchema)
async def cancel_ticket(
    ticket_id: str,
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(get_events_provider_client),
) -> CancelTicketResponseSchema:
    usecase = CancelTicketUseCase(
        session=session,
        events=EventsRepository(session),
        tickets=TicketsRepository(session),
        client=client,
    )
    return await usecase.execute(ticket_id)
