from datetime import datetime

from sqlalchemy import String, func, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base import Base


class SSLCertificateModel(Base):
    __tablename__ = "ssl_certificates"

    __table_args__ = (
        UniqueConstraint("serial_number", "issuer", name="uq_serial_issuer"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    serial_number: Mapped[str] = mapped_column(String(255))
    issuer: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    not_before: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    not_after: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    public_key: Mapped[str] = mapped_column(String(800))

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
