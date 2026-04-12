from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from typing import List
from core.database import get_db
from models.order import (
    Order as OrderModel,
    OrderItem as OrderItemModel,
    Coupon,
    OrderStatus,
)
from schemas.order import (
    OrderCreate,
    Order as OrderSchema,
    OrderStatusUpdate,
)
from models.product import Product as ProductModel
from models.user import User as UserModel
from api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

# --------- UTILIDAD: Cálculo de descuento ---------
def calculate_discount(coupon, subtotal):
    if coupon.discount_type == "percentage":
        return round(subtotal * coupon.discount_value / 100, 2)
    elif coupon.discount_type == "fixed":
        return min(subtotal, coupon.discount_value)
    return 0.0

# ----------- VALIDACIÓN DE CUPONES -----------
class CouponValidateRequest(BaseModel):
    code: str
    cart_total: float

@router.post("/validate")
async def validate_coupon(data: CouponValidateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).where(Coupon.code == data.code.upper().strip()))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupón no encontrado")
    if not coupon.is_active:
        raise HTTPException(status_code=400, detail="Cupón inactivo")
    now = datetime.utcnow()
    if coupon.expires_at and now > coupon.expires_at:
        raise HTTPException(status_code=400, detail="Cupón expirado")
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        raise HTTPException(status_code=400, detail="Límite de usos alcanzado")
    if coupon.minimum_amount and data.cart_total < coupon.minimum_amount:
        raise HTTPException(status_code=400, detail=f"Compra mínima: ${coupon.minimum_amount}")
    return {
        "valid": True,
        "discount_value": coupon.discount_value,
        "discount_type": coupon.discount_type,
    }

# ----------- CREACION DE PEDIDOS (con cupón) -----------
@router.post("/", response_model=OrderSchema, status_code=201)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subtotal = 0.0
    product_details_for_items = []

    for item_in_cart in order_data.items:
        result = await db.execute(select(ProductModel).where(ProductModel.id == item_in_cart.product_id))
        product_in_db = result.scalar_one_or_none()
        if not product_in_db:
            raise HTTPException(status_code=404, detail=f"Producto con ID {item_in_cart.product_id} no encontrado.")
        if product_in_db.stock < item_in_cart.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product_in_db.name}.")
        subtotal += product_in_db.price * item_in_cart.quantity
        product_details_for_items.append({
            "product_model": product_in_db,
            "quantity": item_in_cart.quantity
        })

    # --- Cupón: lógica avanzada ---
    coupon_code = getattr(order_data, "coupon_code", None)
    coupon = None
    coupon_discount = 0.0

    if coupon_code:
        coupon_q = await db.execute(select(Coupon).where(Coupon.code == coupon_code.upper().strip()))
        coupon = coupon_q.scalar_one_or_none()
        now = datetime.utcnow()
        if not coupon:
            raise HTTPException(status_code=404, detail="Cupón inválido.")
        if not coupon.is_active:
            raise HTTPException(status_code=400, detail="Cupón inactivo")
        if coupon.expires_at and now > coupon.expires_at:
            raise HTTPException(status_code=400, detail="Cupón expirado")
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            raise HTTPException(status_code=400, detail="Límite de usos alcanzado")
        if coupon.minimum_amount and subtotal < coupon.minimum_amount:
            raise HTTPException(status_code=400, detail=f"Compra mínima: ${coupon.minimum_amount}")
        coupon_discount = calculate_discount(coupon, subtotal)
    else:
        coupon_code = None

    total_amount = max(0.0, subtotal - coupon_discount + (order_data.shipping_cost or 0))

    try:
        order_number = f"GN-{uuid.uuid4().hex[:6].upper()}"
        new_order = OrderModel(
            user_id=current_user.id,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            payment_method=order_data.payment_method,
            shipping_address=order_data.shipping_address,
            shipping_type=order_data.shipping_type,
            shipping_cost=order_data.shipping_cost,
            order_number=order_number,
            coupon_code=coupon_code,
            coupon_discount_applied=coupon_discount
        )
        db.add(new_order)
        await db.flush()

        for detail in product_details_for_items:
            product = detail["product_model"]
            quantity = detail["quantity"]
            line_total = product.price * quantity
            order_item = OrderItemModel(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity,
                product_name=product.name,
                product_price=product.price,
                line_total=line_total
            )
            db.add(order_item)
            product.stock -= quantity

        # Marcar uso cupón si se usó
        if coupon:
            coupon.used_count += 1

        await db.commit()
        query = (
            select(OrderModel)
            .options(
                joinedload(OrderModel.user),
                joinedload(OrderModel.items).joinedload(OrderItemModel.product)
            )
            .where(OrderModel.id == new_order.id)
        )
        result = await db.execute(query)
        order_fresh = result.unique().scalars().first()
        return order_fresh

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al crear el pedido: {e}")

# ----------- LISTADO Y DETALLE DE PEDIDOS -----------
@router.get("/", response_model=List[OrderSchema])
async def get_all_orders(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    query = (
        select(OrderModel)
        .options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.items).joinedload(OrderItemModel.product)
        )
        .where(OrderModel.user_id == current_user.id)
        .order_by(OrderModel.created_at.desc())
    )
    result = await db.execute(query)
    orders = result.unique().scalars().all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    query = (
        select(OrderModel)
        .options(
            joinedload(OrderModel.items).joinedload(OrderItemModel.product),
            joinedload(OrderModel.user),
        )
        .where(OrderModel.id == order_id, OrderModel.user_id == current_user.id)
    )
    result = await db.execute(query)
    order = result.unique().scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order

@router.patch("/{order_id}/status", response_model=OrderSchema)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(OrderModel).where(OrderModel.id == order_id))
    db_order = result.scalar_one_or_none()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    db_order.status = OrderStatus[status_update.status.upper()]
    await db.commit()
    await db.refresh(db_order)
    return db_order

# ----------- PEDIDOS PARA ADMIN -----------
@router.get("/admin", response_model=List[OrderSchema])
async def get_all_orders_admin(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if getattr(current_user, "role", None) != "ADMIN":
        raise HTTPException(status_code=403, detail="No autorizado")
    query = (
        select(OrderModel)
        .options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.items).joinedload(OrderItemModel.product)
        )
        .order_by(OrderModel.created_at.desc())
    )
    result = await db.execute(query)
    orders = result.unique().scalars().all()
    return orders
