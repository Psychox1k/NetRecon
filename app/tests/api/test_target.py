import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_create_target_api(client: AsyncClient):
    payload = {"name": "Corporate_Network"}
    response = await client.post("/api/v1/targets/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Corporate_Network"


@pytest.mark.asyncio
async def test_get_all_targets(client: AsyncClient, sample_target):
    response = await client.get("/api/v1/targets/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(t["name"] == sample_target.name for t in data)


@pytest.mark.asyncio
async def test_delete_target_api(client: AsyncClient, sample_target):
    response = await client.delete(f"/api/v1/targets/{sample_target.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_res = await client.get(f"/api/v1/targets/{sample_target.id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND
