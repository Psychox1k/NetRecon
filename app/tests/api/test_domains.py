import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_create_domain_api(client: AsyncClient, sample_target):
    """Test creating a domain via the API"""
    payload = {
        "domain_name": "api-test.com",
        "target_id": sample_target.id
    }
    response = await client.post("/api/v1/domains/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["domain_name"] == "api-test.com"
    assert data["target_id"] == sample_target.id


@pytest.mark.asyncio
async def test_get_domain_not_found(client: AsyncClient):
    """Test 404 error for non-existent domain"""
    response = await client.get("/api/v1/domains/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "wasn't FOUND" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_domain_api(client: AsyncClient, sample_domain):
    """Test domain deletion and verify it's gone"""
    # Delete the domain
    delete_res = await client.delete(f"/api/v1/domains/{sample_domain.id}")
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT

    # Try to fetch it again
    get_res = await client.get(f"/api/v1/domains/{sample_domain.id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND
