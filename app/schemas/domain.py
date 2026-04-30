from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.database.models.domain import StatusDomain
from database.models import IPAddressModel


class DomainBase(BaseModel):
    domain_name: str
    status: StatusDomain = StatusDomain.PENDING
    ips: List[IPAddressModel] = []


class DomainCreate(DomainBase):
    target_id: int


class DomainUpdate(DomainBase):
    domain_name: str | None = None
    status: StatusDomain | None = None

class DomainMiniResponse(BaseModel):
    id: int
    domain_name: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class DomainResponse(DomainBase):
    id: int
    target_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)