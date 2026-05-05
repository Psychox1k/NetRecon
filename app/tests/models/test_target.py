import pytest
from app.database.models import TargetModel, TargetStatus


@pytest.mark.asyncio
async def test_target_creation_assignment():
    target = TargetModel(name="test_target", status=TargetStatus.ACTIVE)

    assert target.name == "test_target"
    assert target.status == TargetStatus.ACTIVE


@pytest.mark.asyncio
async def test_target_change_status():
    target = TargetModel(name="test_pause")
    target.status = TargetStatus.PAUSED

    assert target.status == TargetStatus.PAUSED
