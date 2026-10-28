from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.categories.schemas import CategoryCreateSchema, CategoryResponseSchema
from core.database import get_db
from core.dependencies import is_admin
from src.categories.models import Category

router = APIRouter(prefix="/category", tags=["category"])


@router.post("/create",
             status_code=status.HTTP_201_CREATED,
             response_model=CategoryResponseSchema,
             dependencies=[Depends(is_admin)])

async def create_category(
        data: CategoryCreateSchema,
        db: AsyncSession = Depends(get_db)):

    slug = Category.make_slug(data.name)
    result = await db.execute(select(Category).where(Category.name == data.name, Category.slug == slug))
    existing_category = result.scalar_one_or_none()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu nomli categoriya alloqachon mavjud")

    new_category = Category(
        name=data.name,
        slug = slug,
        is_active=data.is_active)

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return new_category


@router.get("/list",
            response_model=List[CategoryResponseSchema],
            status_code=status.HTTP_200_OK)

async def category_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.is_active.is_(True)))
    return result.scalars().all()
