import httpx

from src.events_agg.core.config import settings


class CapashinoClient:
    def __init__(self) -> None:
        self.base_url = settings.capashino_base_url.rstrip("/")
        self.api_key = settings.capashino_api_key

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    async def create_notification(
        self,
        message: str,
        reference_id: str,
        idempotency_key: str,
    ) -> dict:
        url = f"{self.base_url}/api/notifications"
        payload = {
            "message": message,
            "reference_id": reference_id,
            "idempotency_key": idempotency_key,
        }
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
