from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum

# --- ENUM DE ESTADOS DE PEDIDO ---
class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESANDO = "PROCESANDO"
    ENVIADO = "ENVIADO"
    COMPLETADO = "COMPLETADO"
    CANCELADO = "CANCELADO"

# --- MODELO DE PEDIDOS (ORDERS) ---
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_number = Column(String, unique=True, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(String, nullable=False)
    shipping_type = Column(String(20))
    shipping_cost = Column(Float, default=0)
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- CUPÓN USADO EN LA ORDEN ---
    coupon_code = Column(String, ForeignKey("coupons.code"), nullable=True)
    coupon_discount_applied = Column(Float, default=0) # Guarda el monto exacto del descuento

    # Relaciones
    items = relationship("OrderItem", back_populates="order")
    user = relationship("User", back_populates="orders")
    coupon = relationship("Coupon", back_populates="orders", uselist=False, foreign_keys=[coupon_code])

# --- MODELO DE ITEMS DE PEDIDO (ORDER ITEMS) ---
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String, nullable=False)
    product_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    line_total = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

# --- MODELO DE CUPONES (COUPONS) ---
class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_type = Column(String, nullable=False, default="percentage")    # 'percentage' o 'fixed'
    discount_value = Column(Float, nullable=False)                          # 20 = 20% o $20 según tipo
    minimum_amount = Column(Float, default=0)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación reversa para historial de órdenes que usaron este cupón
    orders = relationship("Order", back_populates="coupon", foreign_keys="[Order.coupon_code]", primaryjoin="Order.coupon_code==Coupon.code")
