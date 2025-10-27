# backend/models/user.py

from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum

# ---- Enums (Esto estaba bien) ----
class UserRole(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class AuthProvider(enum.Enum):
    GOOGLE = "GOOGLE"
    EMAIL = "EMAIL"

# --- MODELO DE USUARIO ---
class User(Base):
    # ✅ CORREGIDO: plural y minúscula
    __tablename__ = "users" 

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    provider = Column(Enum(AuthProvider), default=AuthProvider.EMAIL)
    google_id = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones (Esto estaba bien)
    orders = relationship("Order", back_populates="user")
    addresses = relationship("Address", back_populates="user", cascade="all, delete")

# --- MODELO DE DIRECCIÓN ---
class Address(Base):
    # ✅ CORREGIDO: plural y minúscula
    __tablename__ = "addresses" 

    id = Column(Integer, primary_key=True, index=True)
    
    # ✅ CORREGIDO: Apunta a "users.id" (plural y minúscula)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    
    name = Column(String, nullable=True)
    address_line = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, default="México")
    phone = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación (Esto estaba bien)
    user = relationship("User", back_populates="addresses")