from sqlalchemy.exc import IntegrityError

from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import SSLCertificateModel
from app.schemas.ssl_certificate import SSLCertificateResponse, SSLCertificateCreate

router = APIRouter(prefix="/ssl_certificates", tags=["SSL_Certificates"])

@router.get(
    "/",
    response_model=list[SSLCertificateResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_certificates(
        db: AsyncSession = Depends(get_db)
):
    query = select(SSLCertificateModel)
    result = await db.execute(query)

    return result.scalars().all()

@router.get(
    "/{certificate_id}",
    response_model=SSLCertificateResponse,
    status_code=status.HTTP_200_OK
)
async def certificate_get_by_id(
        certificate_id: int,
        db: AsyncSession = Depends(get_db)
):
    query = select(SSLCertificateModel).where(SSLCertificateModel.id == certificate_id)
    result = await db.execute(query)
    db_certificate = result.scalar_one_or_none()

    if not db_certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SSL_Certificates with ID {certificate_id} wasn't not FOUND"
        )

    return db_certificate


@router.post(
    "/",
    response_model=SSLCertificateResponse,
    status_code=status.HTTP_201_CREATED
)
async def certificate_create(
    certificate_in: SSLCertificateCreate,
    db: AsyncSession = Depends(get_db)
):
    query = select(
        SSLCertificateModel
    ).where(
        SSLCertificateModel.serial_number == certificate_in.serial_number,
        SSLCertificateModel.issuer == certificate_in.issuer
    )
    result = await db.execute(query)
    existing_cert = result.scalar_one_or_none()

    if existing_cert:
        return existing_cert

    new_cert = SSLCertificateModel(**certificate_in.model_dump())
    db.add(new_cert)

    try:
        await db.commit()
        await db.refresh(new_cert)
        return new_cert

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Certificate creation failed due to parallel requests"
        )


@router.delete(
    "/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def certificate_delete(
    certificate_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(
        SSLCertificateModel
    ).where(SSLCertificateModel.id == certificate_id)
    result = await db.execute(query)
    db_cert = result.scalar_one_or_none()

    if not db_cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SSL_Certificates with ID {certificate_id} wasn't not FOUND"
        )

    await db.delete(db_cert)
    await db.commit()
