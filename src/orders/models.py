import enum
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreatedBaseModel

if TYPE_CHECKING:
    from src.users.models import User
    from src.addresses.models import Address
    from src.courier.models import CourierProfile
    from src.products.models import Product
    from src.merchant.models import Merchant


class Order(CreatedBaseModel):
    __tablename__ = "orders"

    class OrderStatus(str, enum.Enum):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        PREPARING = "preparing"
        ON_THE_WAY = "on_the_way"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"

    merchant_id: Mapped[UUID] = mapped_column(ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    delivery_address_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"),
                                                                index=True, nullable=True)
    courier_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("couriers.id", ondelete="SET NULL"), index=True,
                                                       nullable=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True,
                                                nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    delivery_address: Mapped[Optional["Address"]] = relationship("Address", back_populates="orders")
    courier: Mapped[Optional["CourierProfile"]] = relationship("CourierProfile", back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates='order')


class OrderItem(CreatedBaseModel):
    __tablename__ = "order_items"

    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True,
                                                       nullable=True)
    product_title: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="order_items",
    )
    products: Mapped[Optional["Product"]] = relationship(
        "Product",
        back_populates="order_items",
    )
