import httpx

from config.settings import settings


class ScanAPIClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL

    async def add_domain(self, domain_name: str, target_id: int):
        endpoint = f"{self.base_url}/domains"

        # This payload exactly matches your DomainCreate Pydantic model
        payload = {
            "domain_name": domain_name,
            "target_id": target_id
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError:
                return None