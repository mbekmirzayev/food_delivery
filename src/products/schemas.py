from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProductCreateSchema(BaseModel):
    title:str = Field(min_length=5, max_length=55)
    category_id : UUID
    merchant_id : UUID
    description: str
    image: str
    price: Decimal
    is_active : bool = Field(default=True)


class ProductResponse(BaseModel):
    id:UUID
    category_id:UUID
    merchant_id : UUID
    title:str = Field(min_length=5, max_length=55)
    description: str
    image: str
    price: Decimal
    is_active : bool = Field(default=True)



