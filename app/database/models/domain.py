from datetime import datetime
import enum

from sqlalchemy import String, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class StatusDomain(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DEAD = "dead"
    IGNORED = "ignored"

class DomainModel(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)

    target_id: Mapped[int] = mapped_column(ForeignKey("targets.id", ondelete="CASCADE"), index=True)
    target: Mapped["TargetModel"] = relationship(back_populates="domains")

    domain_name: Mapped[str] = mapped_column(String(255), unique=True)
    ip_address_v4: Mapped[str | None] = mapped_column(String(15))
    ip_address_v6: Mapped[str | None] = mapped_column(String(39))
    status: Mapped[StatusDomain] = mapped_column(
        Enum(StatusDomain),
            default=StatusDomain.PENDING
    )
    ports: Mapped[list["PortModel"]] = relationship(back_populates="domain")
    certificates: Mapped[list["SSLCertificateModel"]] = relationship(
        secondary="domain_ssl_link",
        back_populates="domains",
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

