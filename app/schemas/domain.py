from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.database.models.domain import StatusDomain
from app.schemas.ssl_certificate import SSLCertificateResponse


class DomainBase(BaseModel):
    domain_name: str
    ip_address_v4: str | None = None
    ip_address_v6: str | None = None
    status: StatusDomain = StatusDomain.PENDING


class DomainCreate(DomainBase):
    target_id: int
    certificate_ids: list[int] = []


class DomainUpdate(DomainBase):
    domain_name: str | None = None
    status: StatusDomain | None = None
    certificate_ids: list[int] | None = None


class DomainResponse(DomainBase):
    id: int
    target_id: int
    created_at: datetime
    updated_at: datetime
    certificates: list[SSLCertificateResponse] = []

    model_config = ConfigDict(from_attributes=True)