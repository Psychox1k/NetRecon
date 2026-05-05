import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_all_ips(client: AsyncClient, sample_ip):
    response = await client.get("/api/v1/ips/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_ip_by_id(client: AsyncClient, sample_ip):
    response = await client.get(f"/api/v1/ips/{sample_ip.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ip"] == "192.168.1.100"


@pytest.mark.asyncio
async def test_get_ip_not_found(client: AsyncClient):
    response = await client.get("/api/v1/ips/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
