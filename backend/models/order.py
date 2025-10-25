# backend/models/order.py

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum


# --- ENUM DE ESTADOS DE PEDIDO ---
class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# --- MODELO DE PEDIDOS (ORDERS) ---
class Order(Base):
    # ✅ CORREGIDO: Debe coincidir con tu tabla en NeonDB
    __tablename__ = "Order" 
    # (Si tu tabla se llama "Orders", pon "Orders" aquí)

    id = Column(Integer, primary_key=True, index=True)
    # ✅ CORREGIDO: La FK debe apuntar a la tabla correcta
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False) 
    order_number = Column(String, unique=True, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(String, nullable=False)
    shipping_type = Column(String(20))
    shipping_cost = Column(Float, default=0)
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    items = relationship("OrderItem", back_populates="order")
    user = relationship("User", back_populates="orders")


# --- MODELO DE ITEMS DE PEDIDO (ORDER ITEMS) ---
class OrderItem(Base):
    # ✅ CORREGIDO:
    __tablename__ = "OrderItem" 
    # (O "OrderItems", como se llame en NeonDB)

    id = Column(Integer, primary_key=True, index=True)
    # ✅ CORREGIDO:
    order_id = Column(Integer, ForeignKey("Order.id"), nullable=False) 
    # ✅ CORREGIDO: (Asegúrate de que 'Product.py' también esté corregido)
    product_id = Column(Integer, ForeignKey("Product.id"), nullable=False) 
    product_name = Column(String, nullable=False)
    product_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    line_total = Column(Float, nullable=False)

    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


# --- MODELO DE CUPONES (COUPONS) ---
class Coupon(Base):
    # ✅ CORREGIDO:
    __tablename__ = "Coupon" 
    # (O "Coupons", como se llame en NeonDB)

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    discount_type = Column(String, nullable=False)
    discount_value = Column(Float, nullable=False)
    minimum_amount = Column(Float, default=0)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())