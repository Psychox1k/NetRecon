import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models import (
    DomainModel,
    IPAddressModel,
    SSLCertificateModel,
    PortModel
)


@pytest.mark.asyncio
async def test_full_chain_loading(db_session, sample_domain):
    ip = IPAddressModel(
        ip="1.1.1.1",
        version="ipv4",
        domain_id=sample_domain.id
    )
    db_session.add(ip)
    await db_session.flush()

    port = PortModel(port_number=80, ip_id=ip.id)
    cert = SSLCertificateModel(issuer="Test", ip_id=ip.id)
    db_session.add_all([port, cert])
    await db_session.commit()

    query = select(DomainModel).where(
        DomainModel.id == sample_domain.id
    ).options(
        selectinload(DomainModel.ips).selectinload(IPAddressModel.ports),
        selectinload(DomainModel.ips).selectinload(IPAddressModel.certificate)
    )
    result = await db_session.execute(query)
    domain = result.scalar_one()

    assert len(domain.ips) == 1
    assert len(domain.ips[0].ports) == 1
    assert domain.ips[0].certificate.issuer == "Test"
