from datetime import datetime
from pydantic import BaseModel


class PlaceShortSchema(BaseModel):
    id: int
    name: str
    city: str
    address: str


class PlaceSchema(PlaceShortSchema):
    seats_pattern: str


class EventListItemSchema(BaseModel):
    id: int
    name: str
    place: PlaceShortSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class EventDeatailSchema(BaseModel):
    id: int
    name: str
    place: PlaceSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class PaginatedEventsSchema(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventListItemSchema]
