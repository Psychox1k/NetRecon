from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Text

from app.database.models.port import PortStatus


class PortBase(BaseModel):
    port_number: int
    service_name: str | None = None
    service_version: str | None = None
    banner: str | None = None
    status: PortStatus = PortStatus.OPEN


class PortCreate(PortBase):
    domain_id: int

class PortResponse(PortBase):
    id: int
    domain_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)