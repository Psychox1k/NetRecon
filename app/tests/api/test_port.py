import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_create_port_api(client: AsyncClient, sample_ip):
    payload = {
        "port_number": 8080,
        "status": "closed",
        "ip_id": sample_ip.id
    }
    response = await client.post("/api/v1/ports/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["port_number"] == 8080

@pytest.mark.asyncio
async def test_create_duplicate_port(client: AsyncClient, sample_port):
    payload = {
        "port_number": sample_port.port_number, # 443 из фикстуры
        "status": "open",
        "ip_id": sample_port.ip_id
    }
    response = await client.post("/api/v1/ports/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_delete_port_api(client: AsyncClient, sample_port):
    response = await client.delete(f"/api/v1/ports/{sample_port.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT