from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.order import Order, OrderItem, Coupon
from models.product import Product
from models.user import User
from schemas.order import OrderCreate, OrderItemCreate
from datetime import datetime

async def get_coupon_by_code(db: AsyncSession, code: str) -> Coupon:
    result = await db.execute(
        select(Coupon).where(Coupon.code == code.upper().strip())
    )
    coupon = result.scalar_one_or_none()
    return coupon

def calculate_discount(coupon: Coupon, cart_total: float) -> float:
    if coupon.discount_type == "percentage":
        return cart_total * (coupon.discount_value / 100)
    elif coupon.discount_type == "fixed":
        return min(cart_total, coupon.discount_value)
    return 0

async def create_order(db: AsyncSession, user: User, data: OrderCreate):
    # Calcula subtotal antes de descuento
    products = {}  # Dict para buscar rápido
    if data.items:
        prod_ids = [oi.product_id for oi in data.items]
        prod_result = await db.execute(
            select(Product).where(Product.id.in_(prod_ids))
        )
        products = {prod.id: prod for prod in prod_result.scalars()}

    subtotal = 0
    order_items = []
    for item in data.items:
        product = products.get(item.product_id)
        if not product:
            raise ValueError(f"Producto con ID {item.product_id} no encontrado")
        line_total = product.price * item.quantity
        subtotal += line_total
        order_items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            quantity=item.quantity,
            line_total=line_total
        ))

    # --- Lógica para cupón ---
    coupon = None
    coupon_discount = 0
    coupon_code = None
    if data.coupon_code:
        coupon = await get_coupon_by_code(db, data.coupon_code)
        today = datetime.now()
        if (not coupon) or (not coupon.is_active):
            raise ValueError("Cupón inválido")
        if coupon.expires_at and today > coupon.expires_at:
            raise ValueError("Tu cupón ha expirado")
        if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
            raise ValueError("Tu cupón ya fue usado el número máximo de veces")
        if coupon.minimum_amount and subtotal < coupon.minimum_amount:
            raise ValueError(f"Tu compra mínima para este cupón es de ${coupon.minimum_amount}")
        coupon_discount = calculate_discount(coupon, subtotal)
        coupon_code = coupon.code

    # Crea la orden
    order = Order(
        user_id=user.id,
        order_number=f"GN{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        status="PENDING",
        total_amount=max(0, subtotal - coupon_discount + (data.shipping_cost or 0)),  # Aplica descuento/costo envío
        shipping_address=data.shipping_address,
        shipping_type=data.shipping_type,
        shipping_cost=data.shipping_cost,
        payment_method=data.payment_method,
        coupon_code=coupon_code,
        coupon_discount_applied=coupon_discount,
        items=order_items
    )

    db.add(order)

    # Marca cupón usado si hay
    if coupon:
        coupon.used_count += 1

    await db.commit()
    await db.refresh(order)
    return order

async def list_orders_for_user(db: AsyncSession, user: User):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

async def get_order(db: AsyncSession, order_id: int, user: User = None):
    q = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    if user:
        q = q.where(Order.user_id == user.id)
    result = await db.execute(q)
    return result.scalar_one_or_none()
