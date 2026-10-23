from typing import List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.products.models import Product
from src.base.models import CreatedBaseModel
from src.users.models import User

if TYPE_CHECKING:
    from src.users.models import User
    from src.products.models import Product

class Cart(CreatedBaseModel):
    __tablename__ = "carts"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True,
                                          nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="cart")
    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="cart")


class CartItem(CreatedBaseModel):
    __tablename__ = "cart_items"

    cart_id: Mapped[UUID] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_items")
    products: Mapped["Product"] = relationship("Product", back_populates="cart_items")
