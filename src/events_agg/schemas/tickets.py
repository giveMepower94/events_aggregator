from pydantic import BaseModel, Field, EmailStr


class CreateTicketRequestSchema(BaseModel):
    event_id: str
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    seat: str = Field(min_length=1, max_length=50)


class CreateTicketResponseSchema(BaseModel):
    ticket_id: str


class CancelTicketResponseSchema(BaseModel):
    success: bool
