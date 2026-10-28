import enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict



class RoleEnum(str, enum.Enum):
    CUSTOMER = "customer"
    COURIER = "courier"
    MERCHANT = 'merchant'
    ADMIN = 'admin'


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:UUID
    first_name:str
    last_name:str
    phone:str
    role:RoleEnum
