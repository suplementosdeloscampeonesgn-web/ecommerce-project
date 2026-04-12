from datetime import date, datetime
from pydantic import BaseModel, Field, constr
from typing import Optional

class CouponBase(BaseModel):
    code: constr(strip_whitespace=True, max_length=32)
    percent: float = Field(..., gt=0, le=90)
    description: Optional[str] = ""
    is_active: Optional[bool] = True
    start_date: Optional[date]
    end_date: Optional[date]
    usage_limit: Optional[int]
    min_order: Optional[float]

class CouponCreate(CouponBase):
    code: constr(strip_whitespace=True, max_length=32)
    percent: float

class CouponUpdate(CouponBase):
    pass

class CouponRead(CouponBase):
    id: int
    usages: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
