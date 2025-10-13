from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# --- Importaciones Corregidas ---
# Se importan las clases específicas y se les da un alias para claridad
from schemas.order import Order as OrderSchema, OrderStatusUpdate
from models.order import Order as OrderModel, OrderItem
from models.product import Product as ProductModel
from core.database import get_db

router = APIRouter()

# --- Schemas para la creación de pedidos (se reciben del frontend) ---
class CartItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    shippingAddress: str
    items: List[CartItem]

# --- Endpoints de la API ---

@router.get("/", response_model=List[OrderSchema])
async def get_all_orders(db: AsyncSession = Depends(get_db)):
    """
    Obtiene todos los pedidos con sus datos relacionados (cliente y productos).
    Usa 'joinedload' para una carga eficiente y evitar el problema N+1.
    """
    query = (
        select(OrderModel)
        .options(
            joinedload(OrderModel.customer),
            joinedload(OrderModel.items).joinedload(OrderItem.product)
        )
        .order_by(OrderModel.date.desc())
    )
    result = await db.execute(query)
    orders = result.unique().scalars().all()
    
    return orders

@router.post("/", response_model=OrderSchema)
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea una nueva orden a partir de los productos en el carrito.
    """
    total = 0.0
    product_items_to_create = []
    
    # NOTA: Aquí iría la lógica para obtener el usuario autenticado (customer_id).
    # Por ahora, usaremos un ID de cliente de ejemplo (ej. el primer usuario).
    customer_id_example = 1

    # Itera sobre los items del carrito para calcular el total y verificar stock
    for item in order_data.items:
        result = await db.execute(select(ProductModel).where(ProductModel.id == item.product_id))
        product = result.scalar_one_or_none()
        
        if product is None or product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para el producto: {product.name if product else 'ID desconocido'}")
        
        total += product.price * item.quantity
        product.stock -= item.quantity  # Reduce el stock del producto
        
        order_item = OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price  # Guarda el precio al momento de la compra
        )
        product_items_to_create.append(order_item)

    # Crea el objeto principal del pedido para la base de datos
    db_order = OrderModel(
        total=total,
        status="Pendiente",
        shippingAddress=order_data.shippingAddress,
        customer_id=customer_id_example,
        items=product_items_to_create
    )

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    # Para devolver una respuesta completa, debemos recargar las relaciones
    query = (
        select(OrderModel)
        .where(OrderModel.id == db_order.id)
        .options(
            joinedload(OrderModel.customer),
            joinedload(OrderModel.items).joinedload(OrderItem.product)
        )
    )
    result = await db.execute(query)
    final_order = result.unique().scalar_one()
    
    return final_order

@router.patch("/{order_id}/status", response_model=OrderSchema)
async def update_order_status(order_id: int, status_update: OrderStatusUpdate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza el estado de un pedido específico.
    """
    query = (
        select(OrderModel)
        .where(OrderModel.id == order_id)
        .options(
            joinedload(OrderModel.customer),
            joinedload(OrderModel.items).joinedload(OrderItem.product)
        )
    )
    result = await db.execute(query)
    db_order = result.unique().scalar_one_or_none()

    if db_order is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    db_order.status = status_update.status
    await db.commit()
    await db.refresh(db_order)
    
    return db_order