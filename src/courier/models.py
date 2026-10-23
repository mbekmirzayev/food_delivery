import enum
import uuid
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreatedBaseModel

if TYPE_CHECKING:
    from src.users.models import User
    from src.orders.models import Order


class CourierProfile(CreatedBaseModel):
    __tablename__ = "couriers"

    class VehicleType(str, enum.Enum):
        MOTO = "moto"
        AVTO = "avto"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    vehicle_type: Mapped[VehicleType] = mapped_column(
        Enum(VehicleType),
        default=VehicleType.MOTO,
        nullable=False
    )
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    current_lat: Mapped[float] = mapped_column(Float, nullable=True)
    current_lon: Mapped[float] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="courier_profile")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="courier")
