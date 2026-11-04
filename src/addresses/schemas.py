from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateAddress(BaseModel):
    city: str
    street: str
    home: str
    apartment: str
    latitude: float
    longitude: float



class AddressResponse(BaseModel):
    id: UUID
    user_id: UUID
    city: str
    street: str
    home: str
    apartment: str
    latitude: float
    longitude: float
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
