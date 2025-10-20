from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# ====================================================================
# Schemas para la ENTRADA de datos en la API (Creación)
# ====================================================================

# Esto es lo que el frontend enviará por cada producto en el carrito
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

# Esto es lo que el frontend enviará para crear el pedido completo
class OrderCreate(BaseModel):
    payment_method: str
    shipping_address: str
    items: List[OrderItemCreate]

# ====================================================================
# Schemas para la SALIDA de datos de la API (Respuesta)
# ====================================================================

# Una versión simplificada del schema de Producto para las respuestas
class ProductInOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

# Una versión simplificada del schema de Usuario para las respuestas
class UserInOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str

# Schema para un item individual dentro de un pedido en las respuestas
class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    quantity: int
    product_price: float # Coincide con tu modelo OrderItem
    product: ProductInOrder # Anida el schema del producto

# El schema principal para devolver un pedido completo en las respuestas
class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    total_amount: float     # Coincide con tu modelo Order
    shipping_address: str   # Coincide con tu modelo Order
    created_at: datetime    # Coincide con tu modelo Order
    user: UserInOrder       # Coincide con la relación 'user' en tu modelo
    items: List[OrderItem]  # Anida una lista de items del pedido

# Un schema simple usado solo para recibir la actualización de estado
class OrderStatusUpdate(BaseModel):
    status: str