"""
Port routing module.
Handles all CRUD operations for network ports discovered during scanning.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.database.models import PortModel, IPAddressModel
from app.schemas.port import PortResponse, PortCreate, PortUpdate

router = APIRouter(prefix="")


@router.get(
    "/",
    response_model=list[PortResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all scanned ports",
    description="Retrieve a list of all discovered ports across the"
                " infrastructure. Can be filtered by a specific IP address."
)
async def get_all_ports(
        ip_name: str | None = None,
        db: AsyncSession = Depends(get_db)
):
    query = select(PortModel)
    if ip_name:
        query = query.join(PortModel.ip_address).where(
            IPAddressModel.ip.ilike(f"%{ip_name}%")
        )

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/{port_id}",
    response_model=PortResponse,
    status_code=status.HTTP_200_OK,
    summary="Get port by ID",
    description="Retrieve detailed information about a specific port,"
                " including its service name, version, and banner."
)
async def get_port_by_id(
        port_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(PortModel).where(PortModel.id == port_id)
    result = await db.execute(query)
    db_port = result.scalar_one_or_none()

    if not db_port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Port with ID {port_id} not found"
        )

    return db_port


@router.post(
    "/",
    response_model=PortResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new port record",
    description="Manually add a new port to an existing IP address."
                " Validates against duplicate port entries on the same IP."
)
async def port_create(
        port_in: PortCreate,
        db: AsyncSession = Depends(get_db)
):
    query = select(PortModel).where(
        PortModel.ip_id == port_in.ip_id,
        PortModel.port_number == port_in.port_number
    )
    result = await db.execute(query)

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Port {port_in.port_number} already exists on this IP"
                   f" address"
        )

    new_port = PortModel(**port_in.model_dump())
    db.add(new_port)
    await db.commit()
    await db.refresh(new_port)
    return new_port


@router.patch(
    "/{port_id}",
    response_model=PortResponse,
    status_code=status.HTTP_200_OK,
    summary="Update port details",
    description="Partially update an existing port record"
                " (e.g., updating its state from 'open' to 'filtered',"
                " or changing service banners)."
)
async def update_port(
        port_id: int,
        port_in: PortUpdate,
        db: AsyncSession = Depends(get_db)
):
    db_port = await db.get(PortModel, port_id)
    if not db_port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Port not found"
        )

    update_data = port_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_port, key, value)

    await db.commit()
    await db.refresh(db_port)
    return db_port


@router.delete(
    "/{port_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete port",
    description="Remove a port record from the database."
)
async def delete_port(port_id: int, db: AsyncSession = Depends(get_db)):
    db_port = await db.get(PortModel, port_id)
    if not db_port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Port not found"
        )

    await db.delete(db_port)
    await db.commit()
