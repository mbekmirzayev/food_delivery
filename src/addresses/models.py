import uuid
from typing import List, TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreatedBaseModel

if TYPE_CHECKING:
    from src.users.models import User
    from src.orders.models import Order


class Address(CreatedBaseModel):
    __tablename__ = "addresses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # title: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(100), default="Tashkent", nullable=False)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    apartment: Mapped[str] = mapped_column(String(50), nullable=True)
    latitude: Mapped[str] = mapped_column(Float, nullable=True)
    longitude: Mapped[str] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship("User",
                                        back_populates="addresses",
                                        )
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="delivery_address",
                                                 )
