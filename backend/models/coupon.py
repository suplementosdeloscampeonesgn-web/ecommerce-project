from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base  # Asegúrate que Base existe en tu proyecto

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, nullable=False, index=True)
    percent = Column(Float, nullable=False, default=10.0)  # porcentaje de descuento, ej. 10.0 (máx 90)
    description = Column(String(255), default="")
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, default=func.current_date())
    end_date = Column(Date, nullable=True)
    usage_limit = Column(Integer, nullable=True)    # Máximo de usos (global)
    usages = Column(Integer, default=0)
    min_order = Column(Float, nullable=True)        # Compra mínima
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    # Puedes agregar owner_id, producto_id, user_id, etc para cupones personalizados o por producto

    def is_valid(self, today: date = None) -> bool:
        """Valida la vigencia del cupón"""
        today = today or date.today()
        if not self.is_active:
            return False
        if self.start_date and today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        if self.usage_limit is not None and self.usages >= self.usage_limit:
            return False
        return True

    def apply(self, amount):
        """Calcula total con descuento aplicado"""
        discount = amount * (self.percent / 100)
        return max(0, amount - discount)
