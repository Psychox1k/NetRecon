import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_create_certificate_api(client: AsyncClient, sample_ip):
    payload = {
        "issuer": "Cloudflare",
        "subject": "test.com",
        "serial_number": "CF-12345",
        "ip_id": sample_ip.id
    }
    response = await client.post("/api/v1/certificates/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["issuer"] == "Cloudflare"

@pytest.mark.asyncio
async def test_get_certificate_by_id(client: AsyncClient, sample_certificate):
    response = await client.get(f"/api/v1/certificates/{sample_certificate.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["serial_number"] == "1234567890"

@pytest.mark.asyncio
async def test_delete_certificate_api(client: AsyncClient, sample_certificate):
    response = await client.delete(f"/api/v1/certificates/{sample_certificate.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT