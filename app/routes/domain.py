from sqlalchemy.orm import selectinload

from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import DomainModel, SSLCertificateModel
from app.schemas.domain import DomainResponse, DomainCreate, DomainUpdate

router = APIRouter(prefix="/domains", tags=["Domains"])


@router.get(
    "/",
    response_model=list[DomainResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_domains(
    target_id: int | None = None,
    name_domain: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(DomainModel).options(selectinload(DomainModel.certificates))
    if target_id:
        query = query.where(DomainModel.target_id == target_id)

    if name_domain:
        query = query.where(DomainModel.domain_name.ilike(f"%{name_domain}%"))

    result = await db.execute(query)

    return result.scalars().all()

@router.get(
    "/{domain_id}",
    response_model=DomainResponse,
    status_code=status.HTTP_200_OK
)
async def get_domain_by_id(
        domain_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(
        DomainModel
    ).where(
        DomainModel.id == domain_id
    ).options(
        selectinload(DomainModel.certificates)
    )
    result = await db.execute(query)
    db_domain = result.scalar_one_or_none()

    if not db_domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain with ID {domain_id} wasn't FOUND"
        )

    return db_domain


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DomainResponse
)
async def domain_create(
    domain_in: DomainCreate,
    db: AsyncSession = Depends(get_db)
):
    domain_data = domain_in.model_dump(exclude={"certificate_ids"})
    new_domain = DomainModel(**domain_data)

    if domain_in.certificate_ids:
        cert_query = select(SSLCertificateModel).where(
            SSLCertificateModel.id.in_(domain_in.certificate_ids)
        )
        certs = (await db.execute(cert_query)).scalars().all()
        new_domain.certificates.extend(certs)
    db.add(new_domain)

    await db.commit()

    query = select(
        DomainModel
    ).where(
        DomainModel.id == new_domain.id
                           ).options(
        selectinload(DomainModel.certificates)
    )

    result = await db.execute(query)
    return result.scalar_one()

@router.patch(
    "/{domain_id}",
    response_model=DomainResponse,
    status_code=status.HTTP_200_OK
)
async def domain_update(
        domain_id: int,
        domain_in: DomainUpdate,
        db: AsyncSession = Depends(get_db)
):
    query = select(DomainModel).where(DomainModel.id == domain_id).options(
        selectinload(DomainModel.certificates)
    )

    db_domain = (await db.execute(query)).scalar_one_or_none()

    if not db_domain:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Domain not found"
        )


    updated_data = domain_in.model_dump(
        exclude_unset=True,
        exclude={"certificate_ids"}
    )

    for key, value in updated_data.items():
        setattr(db_domain, key, value)

    if domain_in.certificate_ids is not None:
        cert_query = select(
            SSLCertificateModel
        ).where(SSLCertificateModel.id.in_(domain_in.certificate_ids))
        certs = (await db.execute(cert_query)).scalars().all()

        db_domain.certificates = list(certs)

    await db.commit()

    query = select(DomainModel).where(DomainModel.id == domain_id).options(
        selectinload(DomainModel.certificates)
    )
    result = await db.execute(query)

    return result.scalar_one()

@router.delete(
    "/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_domain(
        domain_id: int,
        db: AsyncSession = Depends(get_db)
):
    db_domain = await db.get(DomainModel, domain_id)
    if not db_domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    await db.delete(db_domain)
    await db.commit()