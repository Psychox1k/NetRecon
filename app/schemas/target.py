from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.database.models import TargetStatus
from app.schemas.domain import DomainMiniResponse


class TargetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
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
