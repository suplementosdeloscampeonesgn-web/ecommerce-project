from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from typing import Dict

router = APIRouter()

# Carrito simple en memoria para pruebas
cart_storage: Dict = {}

@router.get("/")
async def get_cart(db: AsyncSession = Depends(get_db)):
    """Obtener carrito actual"""
    return {"items": [], "total": 0}

@router.post("/add")
async def add_to_cart(product_id: int, quantity: int = 1, db: AsyncSession = Depends(get_db)):
    """Agregar producto al carrito"""
    return {"message": f"Producto {product_id} agregado", "quantity": quantity}
