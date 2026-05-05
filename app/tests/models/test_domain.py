import pytest
import pytest_asyncio
from sqlalchemy import select
from app.database.models import TargetModel, DomainModel


@pytest_asyncio.fixture
async def sample_target(db_session):
    target = TargetModel(name="Auto_sample_test")
    db_session.add(target)
    await db_session.commit()

    return target


@pytest.mark.asyncio
async def test_create_domain(db_session, sample_target):
    domain = DomainModel(domain_name="example.com", target_id=sample_target.id)
    db_session.add(domain)
    await db_session.commit()

    assert domain.id is not None
    assert domain.domain_name == "example.com"
    assert domain.target_id == sample_target.id


@pytest.mark.asyncio
async def test_read_domain(db_session, sample_target):

    domain = DomainModel(domain_name="readme.com", target_id=sample_target.id)
    db_session.add(domain)
    await db_session.commit()

    query = select(DomainModel).where(DomainModel.domain_name == "readme.com")
    result = await db_session.execute(query)
    fetched_domain = result.scalar_one_or_none()

    assert fetched_domain is not None
    assert fetched_domain.id == domain.id
    assert fetched_domain.target_id == sample_target.id


@pytest.mark.asyncio
async def test_update_domain(db_session, sample_target):
    domain = DomainModel(domain_name="readme.com", target_id=sample_target.id)
    db_session.add(domain)
    await db_session.commit()

    domain.domain_name = "new_name.com"
    await db_session.commit()

    fetched_domain = await db_session.get(DomainModel, domain.id)
    assert fetched_domain.domain_name == "new_name.com"


@pytest.mark.asyncio
async def test_delete_domain(db_session, sample_target):
    domain = DomainModel(
        domain_name="delete-me.com",
        target_id=sample_target.id
    )
    db_session.add(domain)
    db_session.commit()

    domain_id = domain.id

    db_session.delete(domain)
    await db_session.commit()

    fetched_domain = await db_session.get(DomainModel, domain_id)
    assert fetched_domain is None
