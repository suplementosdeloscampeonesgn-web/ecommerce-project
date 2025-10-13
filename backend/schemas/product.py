# en backend/schemas/product.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema base con los campos comunes
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str  # <-- CAMBIO: Añadido para consistencia con el modelo
    image_url: Optional[str] = None # <-- CAMBIO: Campo principal para la URL de la imagen

# Schema para la creación de un producto (recibe datos del frontend)
# Hereda de ProductBase y añade los campos específicos de la creación
class ProductCreate(ProductBase):
    slug: Optional[str] = None # Hacemos slug opcional aquí ya que se genera en la API
    sku: Optional[str] = None  # Hacemos sku opcional aquí ya que se genera en la API
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False

# Schema para la actualización (todos los campos son opcionales)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None # <-- CAMBIO: Usamos el campo simple
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

# Schema para las respuestas de la API (lo que se envía de vuelta al frontend)
# Hereda de ProductBase y añade los campos que genera la base de datos
class Product(ProductBase):
    id: int
    slug: str
    sku: str
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True # Permite que Pydantic lea los datos desde el modelo SQLAlchemy