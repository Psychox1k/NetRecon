from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.database.models import IPAddressModel
from app.schemas.ip import IPAddressResponse

router = APIRouter(prefix="/ips", tags=["IPs"])


@router.get(
    "/",
    response_model=list[IPAddressResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_ports(
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
    status_code=status.HTTP_200_OK
)
async def get_ip_by_id(
        ip_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(IPAddressModel).where(IPAddressModel.id == ip_id).options(
            selectinload(IPAddressModel.ports),
            selectinload(IPAddressModel.certificate)
        )

    db_ip = (await db.execute(query)).scalar_one_or_none()

    if not db_ip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP with ID {ip_id} wasn't FOUND"
        )

    return db_ip