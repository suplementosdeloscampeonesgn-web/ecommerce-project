from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.order import Coupon
from pydantic import BaseModel

router = APIRouter()

class CouponValidateRequest(BaseModel):
    code: str
    cart_total: float

@router.post("/validate")
async def validate_coupon(data: CouponValidateRequest, db: AsyncSession = Depends(get_db)):
    coupon = await db.execute(Coupon.__table__.select().where(Coupon.code == data.code))
    coupon = coupon.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupón no encontrado")
    # Validar expiración, usos, mínimo compra aquí (lógica simplificada)
    if coupon.minimum_amount > data.cart_total:
        raise HTTPException(status_code=400, detail="Cart total no cumple mínimo para cupón")
    return {"valid": True, "discount_value": coupon.discount_value, "discount_type": coupon.discount_type}
