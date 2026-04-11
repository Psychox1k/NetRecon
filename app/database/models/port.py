from datetime import datetime
import enum

from sqlalchemy import ForeignKey, String, Enum, DateTime, func, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base

class PortStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"


class PortModel(Base):
    __tablename__ = "ports"

    id: Mapped[int] = mapped_column(primary_key=True)
    port_number: Mapped[int] = mapped_column(index=True)
    service_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    service_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    banner: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PortStatus] = mapped_column(Enum(PortStatus), default=PortStatus.OPEN)

    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), index=True)
    domain: Mapped["DomainModel"] = relationship(back_populates="ports")


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )