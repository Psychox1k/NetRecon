from datetime import datetime

from sqlalchemy import String, func, DateTime,  JSON, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base import Base


class SSLCertificateModel(Base):
    __tablename__ = "ssl_certificates"

    id: Mapped[int] = mapped_column(primary_key=True)

    ip_id: Mapped[int] = mapped_column(
        ForeignKey(
            "ip_addresses.id",
            ondelete="CASCADE"
        ),
            unique=True,
            index=True
    )

    serial_number: Mapped[str | None] = mapped_column(String(255))
    issuer: Mapped[str | None] = mapped_column(String(255))
    subject: Mapped[str | None] = mapped_column(String(255))
    not_before: Mapped[str | None] = mapped_column(String(100))
    not_after: Mapped[str | None] = mapped_column(String(100))
    public_key: Mapped[str | None] = mapped_column(String(800))

    subdomains: Mapped[list[str]] = mapped_column(JSON, default=list)
    ip_address: Mapped["IPAddressModel"] = relationship(back_populates="certificate")


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
