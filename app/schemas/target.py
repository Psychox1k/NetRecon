from datetime import datetime
from pydantic import BaseModel, ConfigDict

from database.models.target import TargetStatus
from schemas.domain import DomainMiniResponse


class TargetBase(BaseModel):
    name: str
    status: TargetStatus = TargetStatus.ACTIVE


class TargetCreate(TargetBase):
    pass


class TargetUpdate(BaseModel):
    name: str | None = None
    status: TargetStatus | None = None

class TargetResponse(TargetBase):
    id: int

    created_at: datetime
    updated_at: datetime
    domains: list[DomainMiniResponse] = []

    model_config = ConfigDict(from_attributes=True)
