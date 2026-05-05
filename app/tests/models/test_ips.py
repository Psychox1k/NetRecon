import pytest

from app.database.models import IPAddressModel
from database.models import PortModel


@pytest.mark.asyncio
async def test_ip_model_constraints(db_session, sample_domain):
    ip = IPAddressModel(ip="1.1.1.1", version="ipv4", domain_id=sample_domain.id)
    db_session.add(ip)
    await db_session.commit()

    assert ip.version == "ipv4"
    assert ip.domain_id == sample_domain.id


@pytest.mark.asyncio
async def test_create_ip_and_ports(db_session, sample_domain):
    ip = IPAddressModel(ip="45.33.32.156", version="ipv4", domain_id=sample_domain.id)
    db_session.add(ip)
    await db_session.flush()

    port_80 = PortModel(port_number=80, banner="nginx", ip_id=ip.id)
    port_443 = PortModel(port_number=443, banner="OpenSSL", ip_id=ip.id)

    db_session.add_all([port_443, port_80])
    await db_session.commit()

    assert ip.id is not None
    assert port_80.id is not None
    assert port_443.port_number == 443

