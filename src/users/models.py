import enum
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreatedBaseModel

if TYPE_CHECKING:
    from src.orders.models import Order
    from src.addresses.models import Address
    from src.cart.models import Cart
    from src.courier.models import CourierProfile
    from src.merchant.models import Merchant


class User(CreatedBaseModel):
    __tablename__ = "users"

    class UserRole(str, enum.Enum):
        CUSTOMER = "customer"
        COURIER = "courier"
        ADMIN = "admin"
        MERCHANT = "merchant"

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.CUSTOMER,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    addresses: Mapped[List["Address"]] = relationship(
        "Address",
        back_populates="user"
    )
    cart: Mapped[Optional["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        uselist=False
    )
    courier_profile: Mapped[Optional["CourierProfile"]] = relationship(
        "CourierProfile",
        back_populates="user",
        uselist=False
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user"
    )

    merchant : Mapped["Merchant"] = relationship("Merchant", back_populates="user")