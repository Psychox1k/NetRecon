from datetime import datetime

from sqlalchemy import String, func, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column

from . import DomainModel
from .base import Base


class SSLCertificateModel(Base):
    __tablename__ = "ssl_certificates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    serial_number: Mapped[str] = mapped_column(String(255))
    issuer: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    not_before: Mapped[datetime] = mapped_column()
    not_after: Mapped[datetime] = mapped_column()
    public_key: Mapped[str] = mapped_column(String(255), nullable=False)

    domains: Mapped[list["DomainModel"]] = relationship(
        secondary="domain_ssl_link",
        back_populates="certificates",
        lazy="selectin"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
