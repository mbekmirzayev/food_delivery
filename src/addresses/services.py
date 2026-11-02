from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from addresses.models import Address


async def get_address_or_404(address_id: UUID, db:AsyncSession) -> Address:
    address = await db.get(Address, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Joylashuv haqida malumot topilmadi")
    return address