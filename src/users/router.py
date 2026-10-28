# from fastapi import APIRouter, Depends
# from sqlalchemy import Select
# from sqlalchemy.ext.asyncio import AsyncSession
# from starlette import status
#
# from core.database import get_db
# from users.schemas import UserProfile
#
# router = APIRouter(prefix="/profile", tags=["PROFILE"])
#
#
# @router.get("/profile",
#             status_code=status.HTTP_200_OK,
#             response_model=UserProfile)
#
# async def get_profile(db: AsyncSession = Depends(get_db)):
#     res = await db.execute(Select)
