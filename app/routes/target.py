from http.client import responses

from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import TargetModel
from app.schemas.target import TargetResponse, TargetCreate, TargetUpdate

router = APIRouter(prefix="/targets", tags=["Targets"])


@router.get(
    "/",
    response_model=list[TargetResponse],
    status_code=status.HTTP_200_OK,
)
async def all_targets_retrieve(
        name: str | None = None,
        db: AsyncSession = Depends(get_db)
):
    query = select(TargetModel)

    if name:
        query = query.where(TargetModel.name.ilike(f"%{name}%"))

    result = await db.execute(query)

    return result.scalars().all()


@router.get(
    "/{target_id}",
    response_model=TargetResponse,
    status_code=status.HTTP_200_OK
)
async def get_target_by_id(
        target_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(TargetModel).where(TargetModel.id == target_id)
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
    status_code=status.HTTP_201_CREATED
)
async def target_create(
        target_in: TargetCreate,
        db: AsyncSession = Depends(get_db)
):
    new_target = TargetModel(**target_in.model_dump())
    db.add(new_target)
    await db.commit()

    await db.refresh(new_target)

    return new_target



@router.patch(
    "/{target_id}",
    response_model=TargetResponse,
    status_code=status.HTTP_200_OK
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
    await db.refresh(db_target)

    return db_target



@router.delete(
    "/{target_id}",
    status_code=status.HTTP_204_NO_CONTENT
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


