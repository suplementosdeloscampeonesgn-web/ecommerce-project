from sqlalchemy import Column, Integer, String, Float, Boolean, Text, TIMESTAMP, text
from core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=False)
    price = Column(Float, nullable=False)
    
    # --- CAMBIOS PRINCIPALES AQUÍ ---
    # Almacenamos la URL de Firebase directamente en un campo de texto simple.
    # Es más eficiente y mucho más fácil de manejar.
    image_url = Column(String(255), nullable=True) 

    sku = Column(String(100), nullable=False, unique=True)
    stock = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Corregido para que se actualice automáticamente en cada modificación
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=text('now()'))

    # Se eliminaron los campos `compare_price` e `images` que no se usaban o fueron reemplazados.
