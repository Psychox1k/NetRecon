import pytest
import pytest_asyncio

from app.database.models import IPAddressModel, SSLCertificateModel, PortModel
@pytest.mark.asyncio
async def test_port_model_logic(db_session, sample_domain):

    ip = IPAddressModel(ip="192.168.1.1", version="ipv4", domain_id=sample_domain.id)
    db_session.add(ip)
    await db_session.flush()

    port = PortModel(port_number=443, banner="OpenSSL 3.0", ip_id=ip.id)
    db_session.add(port)
    await db_session.commit()

    assert port.port_number == 443
    assert port.ip_id == ip.id


@pytest.mark.asyncio
async def test_create_ssl_certificate(db_session, sample_domain):
    ip = IPAddressModel(ip="45.33.32.156", version="ipv4", domain_id=sample_domain.id)
    db_session.add(ip)
    await db_session.flush()

    cert = SSLCertificateModel(
        issuer="Let's Encrypt",
        subject="scanme.nmap.org",
        serial_number="1234567890",
        ip_id=ip.id
    )

    db_session.add(cert)
    await db_session.commit()

    assert cert.id is not None
    assert cert.issuer == "Let's Encrypt"
    assert cert.ip_id == ip.id

