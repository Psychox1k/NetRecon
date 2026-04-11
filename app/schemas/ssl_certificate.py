from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SSLCertificateBase(BaseModel):
    serial_number: str
    issuer: str
    subject: str
    not_before: datetime
    not_after: datetime
    public_key: str

class SSLCertificateCreate(SSLCertificateBase):
    pass

class SSLCertificateResponse(SSLCertificateBase):
    id: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)