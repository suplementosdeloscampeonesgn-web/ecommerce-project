from sqlalchemy.orm import Session
from datetime import date
from .models.coupon import Coupon
from .schemas.coupon import CouponCreate, CouponUpdate

def get_coupon_by_code(db: Session, code: str):
    return db.query(Coupon).filter(Coupon.code == code.upper().strip()).first()

def create_coupon(db: Session, coupon_data: CouponCreate):
    db_coupon = Coupon(**coupon_data.dict())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def update_coupon(db: Session, db_coupon: Coupon, coupon_data: CouponUpdate):
    for k, v in coupon_data.dict(exclude_unset=True).items():
        setattr(db_coupon, k, v)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def list_coupons(db: Session, skip:int=0, limit:int=100):
    return db.query(Coupon).order_by(Coupon.created_at.desc()).offset(skip).limit(limit).all()

def delete_coupon(db: Session, db_coupon: Coupon):
    db.delete(db_coupon)
    db.commit()

def validate_coupon(db_coupon: Coupon, order_total: float) -> bool:
    return db_coupon and db_coupon.is_valid() and (not db_coupon.min_order or order_total >= db_coupon.min_order)
