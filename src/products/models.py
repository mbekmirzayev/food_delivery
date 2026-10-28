from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreatedBaseModel, SlugBaseModel

if TYPE_CHECKING:
    from src.categories.models import Category
    from src.cart.models import CartItem
    from src.orders.models import OrderItem
    from src.merchant.models import Merchant


class Product(CreatedBaseModel, SlugBaseModel):
    __tablename__ = "products"

    category_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    merchant_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
    )
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        back_populates="products",
    )
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="products",
    )
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="products")
