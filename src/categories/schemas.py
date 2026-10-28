from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CategoryCreateSchema(BaseModel):
    name: str = Field(..., min_length=4, max_length=50)
    is_active: bool = Field(default=True)


class CategoryResponseSchema(BaseModel):
    id: UUID
    name: str
    is_active: bool
    slug : str


    model_config = ConfigDict(from_attributes=True)
