from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List

from schemas.user import AddressRead, AddressCreate
from models.user import Address
from core.database import get_db
from api.auth import get_current_user
from models.user import User

router = APIRouter(
    prefix="/address",
    tags=["Direcciones"],
)

# Listar direcciones del usuario actual
@router.get("/", response_model=List[AddressRead])
async def get_my_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Address).where(Address.user_id == current_user.id)
    result = await db.execute(query)
    addresses = result.scalars().all()
    return addresses

# Crear nueva dirección para el usuario actual
@router.post("/", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_in: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_address = Address(
        user_id=current_user.id,
        **address_in.dict()
    )
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return new_address

# Actualizar dirección por ID
@router.put("/{address_id}", response_model=AddressRead)
async def update_address(
    address_id: int,
    address_in: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Address).where(Address.id == address_id, Address.user_id == current_user.id)
    result = await db.execute(query)
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    for attr, value in address_in.dict().items():
        setattr(address, attr, value)
    await db.commit()
    await db.refresh(address)
    return address

# Eliminar dirección por ID
@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Address).where(Address.id == address_id, Address.user_id == current_user.id)
    result = await db.execute(query)
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="Dirección no encontrada. No se puede borrar.")
    await db.delete(address)
    await db.commit()
    return None
