from pydantic import BaseModel, ConfigDict, constr
from typing import List, Optional
from datetime import datetime
import enum

# --- ENUM MAYÚSCULAS PARA Pydantic ---
class OrderStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    payment_method: str
    shipping_address: str
    shipping_type: str
    shipping_cost: float
    items: List[OrderItemCreate]

class ProductInOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class UserInOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: Optional[str]

class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quantity: int
    product_price: float
    product_id: int
    product_name: str
    product: Optional[ProductInOrder] = None

class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: OrderStatusEnum             # -- Ahora validado con Enum!
    total_amount: float
    shipping_address: str
    shipping_type: str
    shipping_cost: float
    created_at: datetime
    user: UserInOrder
    items: List[OrderItem]

class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum             # -- Ahora validado con Enum (mayúsculas)
