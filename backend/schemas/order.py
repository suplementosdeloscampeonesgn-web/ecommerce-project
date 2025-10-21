from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    payment_method: str
    shipping_address: str
    shipping_type: str      # NUEVO: branch o delivery
    shipping_cost: float    # NUEVO: costo de envío
    items: List[OrderItemCreate]

class ProductInOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class UserInOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str

class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    quantity: int
    product_price: float
    product: ProductInOrder

class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    total_amount: float
    shipping_address: str
    shipping_type: str       # NUEVO
    shipping_cost: float     # NUEVO
    created_at: datetime
    user: UserInOrder
    items: List[OrderItem]

class OrderStatusUpdate(BaseModel):
    status: str
