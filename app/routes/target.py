"""
Target routing module.
Handles CRUD operations for top-level scanning targets
 (projects/infrastructures).
"""
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.database.models import TargetModel, TargetStatus
from app.schemas.target import TargetResponse, TargetCreate, TargetUpdate

router = APIRouter(prefix="")


@router.get(
    "/",
    response_model=list[TargetResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all scanning targets",
    description="Retrieve a list of all defined targets"
                " (projects/infrastructures). Supports"
                " optional filtering by partial name and "
                "current status."
)
async def all_targets_retrieve(
        name: str | None = Query(None, description="Filter by target name"),
        status_filter: TargetStatus | None = Query(
            None, description="Filter by target status"
        ),
        db: AsyncSession = Depends(get_db)
):
    query = select(TargetModel)

    if name:
        query = query.where(TargetModel.name.ilike(f"%{name}%"))

    if status_filter:
        query = query.where(TargetModel.status == status_filter)

    query = query.options(selectinload(TargetModel.domains))

    result = await db.execute(query)

    return result.scalars().all()


@router.get(
    "/{target_id}",
    response_model=TargetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get target by ID",
    description="Retrieve detailed information about a specific target,"
                " including all its associated domains."
)
async def get_target_by_id(
        target_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(TargetModel).where(
        TargetModel.id == target_id
    ).options(selectinload(TargetModel.domains))

    result = await db.execute(query)
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID {target_id} not found"
        )

    return target


@router.post(
    "/",
    response_model=TargetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new target",
    description="Initialize a new target infrastructure for scanning."
                " This acts as a logical container for domains and IPs."
)
async def target_create(
        target_in: TargetCreate,
        db: AsyncSession = Depends(get_db)
):
    new_target = TargetModel(**target_in.model_dump())
    db.add(new_target)
    await db.commit()

    query = select(TargetModel).where(
        TargetModel.id == new_target.id
    ).options(
        selectinload(TargetModel.domains)
    )
    result = await db.execute(query)
    loaded_target = result.scalar_one()

    return loaded_target


@router.patch(
    "/{target_id}",
    response_model=TargetResponse,
    status_code=status.HTTP_200_OK,
    summary="Update target details",
    description="Partially update target information, such as changing its"
                " name or updating its scanning status."
)
async def target_update(
        target_id: int,
        target_in: TargetUpdate,
        db: AsyncSession = Depends(get_db)
):
    query = select(TargetModel).where(TargetModel.id == target_id)
    result = await db.execute(query)
    db_target = result.scalar_one_or_none()

    if not db_target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID {target_id} not found"
        )

    update_data = target_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_target, key, value)

    await db.commit()

    refresh_query = select(TargetModel).where(
        TargetModel.id == target_id
    ).options(selectinload(TargetModel.domains))
    result = await db.execute(refresh_query)
    loaded_target = result.scalar_one()

    return loaded_target


@router.delete(
    "/{target_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete target",
    description="Remove a target entirely. Due to database cascading,"
                " this will permanently delete all associated domains,"
                " IPs, ports, and certificates."
)
async def target_delete_by_id(
        target_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(TargetModel).where(TargetModel.id == target_id)
    result = await db.execute(query)

    db_target = result.scalar_one_or_none()

    if not db_target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID {target_id} not found"
        )

    await db.delete(db_target)
    await db.commit()
