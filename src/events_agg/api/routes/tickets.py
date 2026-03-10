from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.db.session import get_session
from src.events_agg.repositories.events import EventsRepository
from src.events_agg.repositories.tickets import TicketsRepository
from src.events_agg.schemas.tickets import (
    CreateTicketRequestSchema,
    CreateTicketResponseSchema,
    CancelTicketResponseSchema
)
from src.events_agg.usecases.create_ticket import CreateTicketUseCase
from src.events_agg.usecases.cancel_ticket import CancelTicketUseCase


router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=CreateTicketResponseSchema, status_code=201)
async def create_ticket(
    data: CreateTicketRequestSchema,
    session: AsyncSession = Depends(get_session),
) -> CreateTicketResponseSchema:
    usecase = CreateTicketUseCase(
        session=session,
        events=EventsRepository(session),
        tickets=TicketsRepository(session),
        client=EventsProviderClient(),
    )
    return await usecase.execute(data)


@router.delete("/{ticket_id}", response_model=CancelTicketResponseSchema)
async def cancel_ticket(
    ticket_id: str,
    session: AsyncSession = Depends(get_session),
) -> CancelTicketResponseSchema:
    usecase = CancelTicketUseCase(
        session=session,
        events=EventsRepository(session),
        tickets=TicketsRepository(session),
        client=EventsProviderClient(),
    )
    return await usecase.execute(ticket_id)
