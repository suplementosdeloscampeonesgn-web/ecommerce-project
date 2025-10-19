# En: backend/api/categories.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from core.database import get_db
from models.product import Product as ProductModel

router = APIRouter()

@router.get("/", response_model=List[str], tags=["Categories"])
async def get_unique_categories(db: Session = Depends(get_db)):
    """
    Obtiene una lista de todas las categorías de productos únicas.
    """
    try:
        query = select(ProductModel.category).distinct()
        result = await db.execute(query)
        categories_list = result.scalars().all()
        return [category for category in categories_list if category is not None]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))