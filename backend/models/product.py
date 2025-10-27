from sqlalchemy import Column, Integer, String, Float, Boolean, Text, TIMESTAMP, text, ForeignKey
from core.database import Base

class Product(Base):
    # ✅ CORREGIDO: Debe coincidir con tu tabla en NeonDB
    __tablename__ = "products" 
    # (O "Products", si así se llama. Debe ser exacto)

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=False)
    price = Column(Float, nullable=False)
    
    # Esta columna está bien definida
    image_url = Column(String(255), nullable=True) 

    sku = Column(String(100), nullable=False, unique=True)
    stock = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=text('now()'))