from typing import List, TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import SlugBaseModel, CreatedBaseModel

if TYPE_CHECKING:
    from src.products.models import Product


class Category(CreatedBaseModel, SlugBaseModel):
    __tablename__ = 'categories'

    name: Mapped[str] = mapped_column(String(255))
    is_Active: Mapped[bool] = mapped_column(Boolean, default=True)
    products: Mapped[List["Product"]] = relationship(back_populates='category')
