import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.database.models import TargetModel, DomainModel
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_target(db_session):
    target = TargetModel(name="test_target")
    db_session.add(target)
    await db_session.commit()
    return target


@pytest_asyncio.fixture
async def sample_domain(db_session, sample_target):
    domain = DomainModel(domain_name="scanme.nmap.org", target_id=sample_target.id)
    db_session.add(domain)
    await db_session.commit()
    return domain

from app.database.models import IPAddressModel, PortModel, SSLCertificateModel

@pytest_asyncio.fixture
async def sample_ip(db_session, sample_domain):
    ip = IPAddressModel(ip="192.168.1.100", version="ipv4", domain_id=sample_domain.id)
    db_session.add(ip)
    await db_session.commit()
    await db_session.refresh(ip)
    return ip

@pytest_asyncio.fixture
async def sample_port(db_session, sample_ip):
    port = PortModel(port_number=443, status="open", ip_id=sample_ip.id)
    db_session.add(port)
    await db_session.commit()
    await db_session.refresh(port)
    return port

@pytest_asyncio.fixture
async def sample_certificate(db_session, sample_ip):
    cert = SSLCertificateModel(
        issuer="Let's Encrypt",
        subject="api-test.com",
        serial_number="1234567890",
        ip_id=sample_ip.id
    )
    db_session.add(cert)
    await db_session.commit()
    await db_session.refresh(cert)
    return cert