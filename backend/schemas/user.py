from pydantic import BaseModel, EmailStr
from typing import Optional, List

# ---------- Schemas de Direcciones ----------

class AddressBase(BaseModel):
    name: Optional[str] = None        # Ejemplo: "Casa", "Oficina", etc
    address_line: str
    city: str
    state: str
    postal_code: str
    country: Optional[str] = "México"
    phone: Optional[str] = None
    is_default: Optional[bool] = False

class AddressCreate(AddressBase):
    pass

class AddressRead(AddressBase):
    id: int

    class Config:
        from_attributes = True

# ---------- Schemas de Usuario ----------

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    role: str
    provider: str
    is_active: bool
    addresses: Optional[List[AddressRead]] = []   # <-- Lista de direcciones asociadas

    class Config:
        from_attributes = True
