from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .port import PortResponse
from .ssl_certificate import SSLCertificateResponse


class IPAddressBase(BaseModel):
    ip: str
    version: str


class IPAddressCreate(IPAddressBase):
    domain_id: int


class IPAddressRead(IPAddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    certificate: Optional[SSLCertificateResponse] = None
    ports: List[PortResponse] = []



