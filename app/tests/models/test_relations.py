import pytest

from app.database.models import IPAddressModel, SSLCertificateModel, PortModel, TargetModel, DomainModel


@pytest.mark.asyncio
async def test_cascade_delete_magic(db_session, sample_domain, sample_target):
    ip = IPAddressModel(ip="8.8.8.8", version="ipv4", domain_id=sample_domain.id)
    db_session.add(ip)
    await db_session.flush()

    port = PortModel(port_number=22, ip_id=ip.id)
    cert = SSLCertificateModel(issuer="GlobalSign", ip_id=ip.id, serial_number="1234567890", subject="scanme.nmap.org",)
    db_session.add_all([port, cert])
    await db_session.commit()

    target_id = sample_target.id
    domain_id = sample_domain.id
    ip_id = ip.id
    port_id = port.id
    cert_id = cert.id

    await db_session.delete(sample_target)
    await db_session.commit()

    assert await db_session.get(TargetModel, target_id) is None
    assert await db_session.get(DomainModel, domain_id) is None
    assert await db_session.get(IPAddressModel, ip_id) is None
    assert await db_session.get(PortModel, port_id) is None
    assert await db_session.get(SSLCertificateModel, cert_id) is None
