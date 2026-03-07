from pydantic import BaseModel


class EventSeatsResponseSchema(BaseModel):
    event_id: str
    available_seats: list[str]
