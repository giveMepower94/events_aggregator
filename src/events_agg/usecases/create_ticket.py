from datetime import datetime, timezone
import httpx

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.core.idempotency import build_ticket_request_hash
from src.events_agg.core.seats import seat_exists_in_pattern
from src.events_agg.core.state import seats_cache
from src.events_agg.repositories.events import EventsRepository
from src.events_agg.repositories.idempotency import IdempotencyRepository
from src.events_agg.repositories.outbox import OutboxRepository
from src.events_agg.repositories.tickets import TicketsRepository

from src.events_agg.schemas.tickets import CreateTicketRequestSchema, CreateTicketResponseSchema


class CreateTicketUseCase:
    def __init__(
        self,
        session: AsyncSession,
        events: EventsRepository,
        tickets: TicketsRepository,
        outbox: OutboxRepository,
        idempotency: IdempotencyRepository,
        client: EventsProviderClient,
    ) -> None:
        self.session = session
        self.events = events
        self.tickets = tickets
        self.outbox = outbox
        self.idempotency = idempotency
        self.client = client

    async def _resolve_existing_idempotency(
        self,
        idempotency_key: str,
        request_hash: str,
    ) -> CreateTicketResponseSchema:
        existing = await self.idempotency.get_by_key(idempotency_key)
        if existing is None:
            raise HTTPException(
                status_code=500,
                detail="Idempotency state is inconsistent",
            )

        if existing.request_hash != request_hash:
            raise HTTPException(
                status_code=409,
                detail="Idempotency key conflict"
            )

        if existing.status == "completed" and existing.ticket_id:
            return CreateTicketResponseSchema(ticket_id=existing.ticket_id)

        raise HTTPException(
            status_code=409,
            detail="Request with this idempotency_key is already being processed",
        )

    async def execute(
        self,
        data: CreateTicketRequestSchema,
    ) -> CreateTicketResponseSchema:

        request_hash = build_ticket_request_hash(data)
        idempotency_record = None

        if data.idempotency_key:
            existing = await self.idempotency.get_by_key(data.idempotency_key)
            if existing is not None:
                return await self._resolve_existing_idempotency(
                    idempotency_key=data.idempotency_key,
                    request_hash=request_hash,
                )
        try:
            event = await self.events.get(data.event_id)
            if event is None:
                raise HTTPException(status_code=404, detail="Event not found")
            if event.status != "published":
                raise HTTPException(
                    status_code=400,
                    detail="Registration is available only for published events",
                )
            now = datetime.now(timezone.utc)
            event_time = event.event_time
            registration_deadline = event.registration_deadline

            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=timezone.utc)

            if registration_deadline.tzinfo is None:
                registration_deadline = registration_deadline.replace(tzinfo=timezone.utc)

            if now >= registration_deadline:
                raise HTTPException(
                    status_code=400,
                    detail="Registration deadline has passed",
                )

            if now >= event_time:
                raise HTTPException(status_code=400, detail="Event has already started")

            if not seat_exists_in_pattern(data.seat, event.place.seats_pattern):
                raise HTTPException(status_code=400, detail="Seat does not exist")

            seats_response = await self.client.get_seats(data.event_id)
            if data.seat not in seats_response.seats:
                raise HTTPException(status_code=400, detail="Seat is not available")

            if data.idempotency_key:
                try:
                    idempotency_record = await self.idempotency.create_processing(
                        idempotency_key=data.idempotency_key,
                        request_hash=request_hash,
                    )
                except IntegrityError:
                    await self.session.rollback()
                    return await self._resolve_existing_idempotency(
                        idempotency_key=data.idempotency_key,
                        request_hash=request_hash,
                    )
            try:
                provider_response = await self.client.register(
                    event_id=data.event_id,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    email=data.email,
                    seat=data.seat,
                )
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text

                try:
                    payload = exc.response.json()
                    if isinstance(payload, dict):
                        detail = payload.get("detail") or payload.get("message") or detail
                except Exception:
                    pass

                await self.session.rollback()

                if exc.response.status_code == 400:
                    raise HTTPException(status_code=400, detail=detail)

                raise HTTPException(status_code=502, detail="Events Provider error")

            ticket = await self.tickets.create(
                ticket_id=provider_response.ticket_id,
                event_id=data.event_id,
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                seat=data.seat,
            )

            await self.outbox.create_ticket_purchased(
                ticket=ticket,
                event_name=event.name,
            )

            if idempotency_record is not None:
                await self.idempotency.mark_completed(
                    record=idempotency_record,
                    ticket_id=ticket.ticket_id,
                )
            await self.session.commit()

            seats_cache.delete(f"event_seats:{data.event_id}")

            return CreateTicketResponseSchema(ticket_id=provider_response.ticket_id)

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception:
            await self.session.rollback()
            raise
