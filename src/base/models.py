import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDBaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )


class SlugBaseModel(Base):
    __abstract__ = True

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )


class CreatedBaseModel(UUIDBaseModel):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "Base",
    "UUIDBaseModel",
    "SlugBaseModel",
    "CreatedBaseModel",
]
