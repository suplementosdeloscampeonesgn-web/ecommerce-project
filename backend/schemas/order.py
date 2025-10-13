from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# ====================================================================
# Define los schemas para los datos que estarán anidados dentro de "Order"
# ====================================================================

# Una versión simplificada del schema de Producto para usarla en la respuesta del pedido
class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float

# Una versión simplificada del schema de Usuario para mostrar quién hizo el pedido
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str] = None
    email: str

# Schema para un item individual dentro de un pedido
class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quantity: int
    price: float
    product: Product # Anida el schema del producto

# ====================================================================
# Define los schemas principales de la Orden
# ====================================================================

# El schema principal para devolver un pedido completo en las respuestas de la API
class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime
    total: float
    status: str
    shippingAddress: str
    customer: User             # Anida el schema del cliente (usuario)
    items: List[OrderItem]     # Anida una lista de items del pedido

# Un schema simple usado solo para recibir la actualización de estado
class OrderStatusUpdate(BaseModel):
    status: str