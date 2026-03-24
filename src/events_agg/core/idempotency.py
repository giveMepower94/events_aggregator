import hashlib
import json

from src.events_agg.schemas.tickets import CreateTicketRequestSchema


def build_ticket_request_hash(data: CreateTicketRequestSchema) -> str:
    payload = {
        "event_id": data.event_id,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": str(data.email).lower(),
        "seat": data.seat,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
