from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List
import uuid

from schemas.order import OrderCreate, Order as OrderSchema, OrderStatusUpdate
from models.order import Order as OrderModel, OrderItem as OrderItemModel, OrderStatus
from models.product import Product as ProductModel
from models.user import User as UserModel
from core.database import get_db
from api.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=OrderSchema, status_code=201)
async def create_order(
    order_data: OrderCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    total_amount = 0.0
    product_details_for_items = []

    # Valida productos y stock antes de crear orden
    for item_in_cart in order_data.items:
        result = await db.execute(select(ProductModel).where(ProductModel.id == item_in_cart.product_id))
        product_in_db = result.scalar_one_or_none()
        if not product_in_db:
            raise HTTPException(status_code=404, detail=f"Producto con ID {item_in_cart.product_id} no encontrado.")
        if product_in_db.stock < item_in_cart.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product_in_db.name}.")
        total_amount += product_in_db.price * item_in_cart.quantity
        product_details_for_items.append({
            "product_model": product_in_db,
            "quantity": item_in_cart.quantity
        })

    # Suma el costo de envío al total del pedido
    total_amount += order_data.shipping_cost or 0

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
            order_number=order_number
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

        await db.commit()
        await db.refresh(new_order)
        return new_order

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al crear el pedido: {e}")

@router.get("/", response_model=List[OrderSchema])
async def get_all_orders(db: AsyncSession = Depends(get_db)):
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

@router.patch("/{order_id}/status", response_model=OrderSchema)
async def update_order_status(order_id: int, status_update: OrderStatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OrderModel).where(OrderModel.id == order_id))
    db_order = result.scalar_one_or_none()

    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    db_order.status = OrderStatus[status_update.status.upper()]
    await db.commit()
    await db.refresh(db_order)
    return db_order
