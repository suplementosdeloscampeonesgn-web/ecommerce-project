from pydantic import BaseModel, ConfigDict, constr, Field
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
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    payment_method: str
    shipping_address: str
    shipping_type: str
    shipping_cost: float
    items: List[OrderItemCreate]
    coupon_code: Optional[str] = None    # <<<<< ACEPTA cupón opcional desde frontend

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

class CouponInOrder(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    minimum_amount: float
    max_uses: Optional[int]
    used_count: int
    is_active: bool
    expires_at: Optional[datetime]

    class Config:
        orm_mode = True

class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: OrderStatusEnum
    total_amount: float
    shipping_address: str
    shipping_type: str
    shipping_cost: float
    coupon_code: Optional[str] = None       # <<<<< ALMACENA el código usado
    coupon_discount_applied: Optional[float] = 0  # <<<<< Monto descontado en esta orden
    coupon: Optional[CouponInOrder] = None
    created_at: datetime
    user: UserInOrder
    items: List[OrderItem]

class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum
