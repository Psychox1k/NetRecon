"""
IP Address routing module.
Handles retrieval operations for IP Address models.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.database.models import IPAddressModel
from app.schemas.ip import IPAddressResponse

router = APIRouter(prefix="")


@router.get(
    "/",
    response_model=list[IPAddressResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all IP addresses",
    description="Retrieve a list of all IP addresses. Can be optionally"
                " filtered by a partial IP string match."
)
async def get_all_ips(  # Fixed typo: changed from get_all_ports to get_all_ips
    ip_name: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(IPAddressModel).options(
            selectinload(IPAddressModel.ports),
            selectinload(IPAddressModel.certificate)
        )
    if ip_name:
        query = query.where(IPAddressModel.ip.ilike(f"%{ip_name}%"))

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/{ip_id}",
    response_model=IPAddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get IP address by ID",
    description="Retrieve a specific IP address by its unique ID,"
                " including all related open ports and SSL certificate"
                " data."
)
async def get_ip_by_id(
        ip_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(IPAddressModel).where(
        IPAddressModel.id == ip_id
    ).options(
            selectinload(IPAddressModel.ports),
            selectinload(IPAddressModel.certificate)
    )

    db_ip = (await db.execute(query)).scalar_one_or_none()

    if not db_ip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP address with ID {ip_id} not found"
        )

    return db_ip
