from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # <-- 1. Importa 'relationship'
from core.database import Base
import enum

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_number = Column(String, unique=True, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- ✅ RELACIONES AÑADIDAS ---
    # Un pedido (Order) tiene muchos items (OrderItem)
    items = relationship("OrderItem", back_populates="order")
    # Un pedido (Order) pertenece a un usuario (User)
    user = relationship("User", back_populates="orders")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String, nullable=False)
    product_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    line_total = Column(Float, nullable=False)

    # --- ✅ RELACIONES AÑADIDAS ---
    # Un item de pedido (OrderItem) pertenece a un pedido (Order)
    order = relationship("Order", back_populates="items")
    # Un item de pedido (OrderItem) se refiere a un producto (Product)
    product = relationship("Product")

class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    discount_type = Column(String, nullable=False)  # "percentage" o "fixed"
    discount_value = Column(Float, nullable=False)
    minimum_amount = Column(Float, default=0)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())