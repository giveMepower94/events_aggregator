from datetime import datetime
from pydantic import BaseModel


class ProviderPlaceSchema(BaseModel):
    id: str
    name: str
    city: str
    address: str
    seats_pattern: str
    changed_at: datetime
    created_at: datetime


class ProviderEventSchema(BaseModel):
    id: str
    name: str
    place: ProviderPlaceSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime


class ProviderEventsPageSchema(BaseModel):
    next: str | None
    previous: str | None
    results: list[ProviderEventSchema]


class ProviderSeatsSchema(BaseModel):
    seats: list[str]


class ProviderRegisterResponseSchema(BaseModel):
    ticket_id: str


class ProviderUnregisterResponseSchema(BaseModel):
    success: bool
