from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreatedBaseModel, SlugBaseModel

if TYPE_CHECKING:
    from src.products.models import Product
    from src.users.models import User
    from src.orders.models import Order

class Merchant(CreatedBaseModel, SlugBaseModel):
    __tablename__ = 'merchants'

    business_name: Mapped[str] = mapped_column(String(255), unique=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False, index=True)

    products : Mapped[List["Product"]] = relationship("Product", back_populates="merchant")
    user : Mapped["User"] = relationship("User", back_populates="merchant")
    order : Mapped[List["Order"]] = relationship("Order", back_populates="merchant")