from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class MerchantCreateSchema(BaseModel):
    user_id: UUID
    business_name : str = Field(min_length=5, max_length=255)

class MerchantResponse(BaseModel):
    id: UUID
    user_id : UUID
    business_name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)
