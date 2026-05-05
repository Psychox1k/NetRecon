from datetime import datetime

from sqlalchemy import String, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
import enum

class TargetStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"

class TargetModel(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    domains: Mapped[list["DomainModel"]] = relationship(back_populates="target", cascade="all, delete-orphan")

    status: Mapped[TargetStatus] = mapped_column(
        Enum(TargetStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=TargetStatus.ACTIVE,
        server_default=TargetStatus.ACTIVE.value
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