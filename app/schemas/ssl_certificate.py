from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SSLCertificateBase(BaseModel):
    serial_number: str | None = None
    issuer: str | None = None
    subject: str | None = None
    not_before: str | None = None
    not_after: str | None = None
    public_key: str | None = None
    subdomains: list[str] = []

class SSLCertificateCreate(SSLCertificateBase):
    ip_id: int

class SSLCertificateResponse(SSLCertificateBase):
    id: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)