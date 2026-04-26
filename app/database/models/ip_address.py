from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class IPAddressModel(Base):
    __tablename__ = "ip_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), index=True)

    ip: Mapped[str] = mapped_column(String(50), index=True)
    version: Mapped[str] = mapped_column(String(10))

    domain: Mapped["DomainModel"] = relationship(back_populates="ips")
    ports: Mapped[list["PortModel"]] = relationship(
        back_populates="ip_address",
        cascade="all, delete-orphan"
    )


    certificate: Mapped["SSLCertificateModel"] = relationship(
        back_populates="ip_address",
        uselist=False,
        cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())