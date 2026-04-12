from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import PortModel
from app.schemas.port import PortResponse, PortCreate, PortUpdate

router = APIRouter(prefix="/ports", tags=["Ports"])

@router.get(
    "/",
    response_model=list[PortResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_ports(
    domain_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(PortModel)
    if domain_id:
        query = query.where(PortModel.domain_id == domain_id)

    result = await db.execute(query)
    return result.scalars().all()

@router.get(
    "/{port_id}",
    response_model=PortResponse,
    status_code=status.HTTP_200_OK
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
            detail=f"Port with ID {port_id} wasn't FOUND"
        )

    return db_port

@router.post(
    "/",
    response_model=PortResponse,
    status_code=status.HTTP_201_CREATED
)
async def port_create(
        port_in: PortCreate,
        db: AsyncSession = Depends(get_db)
):
    query = select(PortModel).where(
        PortModel.domain_id == port_in.domain_id,
        PortModel.port_number == port_in.port_number
    )
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Port {port_in.port_number} already exists on this domain"
        )

    new_port = PortModel(**port_in.model_dump())
    db.add(new_port)
    await db.commit()
    await db.refresh(new_port)
    return new_port

@router.patch("/{port_id}", response_model=PortResponse)
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


@router.delete("/{port_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_port(port_id: int, db: AsyncSession = Depends(get_db)):
    db_port = await db.get(PortModel, port_id)
    if not db_port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Port not found"
        )

    await db.delete(db_port)
    await db.commit()