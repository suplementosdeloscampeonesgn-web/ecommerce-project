from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.coupon import Coupon  # asegúrate que importas tu modelo correcto
from pydantic import BaseModel
from datetime import date

router = APIRouter()

class CouponValidateRequest(BaseModel):
    code: str
    cart_total: float

class CouponValidateResponse(BaseModel):
    valid: bool
    message: str = ""
    discount_value: float = 0.0
    percent: float = 0.0
    min_order: float = 0.0
    end_date: date | None = None

@router.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(data: CouponValidateRequest, db: AsyncSession = Depends(get_db)):
    query = select(Coupon).where(Coupon.code == data.code.upper())
    result = await db.execute(query)
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupón no encontrado")

    today = date.today()
    if not coupon.is_active:
        raise HTTPException(status_code=400, detail="El cupón está inactivo")
    if coupon.start_date and today < coupon.start_date:
        raise HTTPException(status_code=400, detail="El cupón aún no es válido")
    if coupon.end_date and today > coupon.end_date:
        raise HTTPException(status_code=400, detail="El cupón está expirado")
    if coupon.usage_limit is not None and coupon.usages >= coupon.usage_limit:
        raise HTTPException(status_code=400, detail="El cupón ha alcanzado su límite de usos")
    if coupon.min_order and data.cart_total < coupon.min_order:
        raise HTTPException(status_code=400, detail=f"Monto mínimo para aplicar el cupón: ${coupon.min_order:,.2f}")

    # Si todo es válido:
    return CouponValidateResponse(
        valid=True,
        message=f"Cupón válido: {coupon.percent}% de descuento",
        discount_value=data.cart_total * coupon.percent / 100,
        percent=coupon.percent,
        min_order=coupon.min_order or 0.0,
        end_date=coupon.end_date
    )

# ---------- Endpoints pro (admin) ----------
from schemas.coupon import CouponCreate, CouponUpdate, CouponRead

@router.post("/", response_model=CouponRead, status_code=status.HTTP_201_CREATED)
async def create_coupon(coupon: CouponCreate, db: AsyncSession = Depends(get_db)):
    # Agrega validación de unicidad, rangos extra si lo deseas
    db_coupon = Coupon(**coupon.dict())
    db.add(db_coupon)
    await db.commit()
    await db.refresh(db_coupon)
    return db_coupon

@router.get("/", response_model=list[CouponRead])
async def list_coupons(skip:int=0, limit:int=100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).order_by(Coupon.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

@router.put("/{coupon_id}", response_model=CouponRead)
async def update_coupon(coupon_id: int, update: CouponUpdate, db: AsyncSession = Depends(get_db)):
    coupon = await db.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupón no encontrado")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(coupon, k, v)
    await db.commit()
    await db.refresh(coupon)
    return coupon

@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(coupon_id: int, db: AsyncSession = Depends(get_db)):
    coupon = await db.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupón no encontrado")
    await db.delete(coupon)
    await db.commit()
