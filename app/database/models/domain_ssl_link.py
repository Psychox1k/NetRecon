from sqlalchemy import Column, ForeignKey, Table
from .base import Base


domain_ssl_link = Table(
    "domain_ssl_link",
    Base.metadata,
    Column("domain_id", ForeignKey("domains.id", ondelete="CASCADE"), primary_key=True),
    Column("certificate_id", ForeignKey("ssl_certificates.id", ondelete="CASCADE"), primary_key=True)
)