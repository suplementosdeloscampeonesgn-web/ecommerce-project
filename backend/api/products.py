from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

# --- CAMBIO: Importa los schemas específicos para cada operación ---
from models.product import Product as ProductModel 
from schemas.product import ProductCreate, ProductUpdate, Product as ProductSchema
from core.database import get_db

router = APIRouter(
    tags=["Products"]
)

@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: Session = Depends(get_db)):
    query = select(ProductModel)
    result = await db.execute(query)
    products = result.scalars().all()
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(ProductModel).where(ProductModel.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.post("/", response_model=ProductSchema, status_code=201)
async def create_product(
    product: ProductCreate, # <-- CAMBIO: Usa el schema ProductCreate para la entrada
    db: Session = Depends(get_db)
):
    slug = product.name.lower().replace(" ", "-") + f"-{uuid.uuid4().hex[:6]}"
    sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"

    db_product = ProductModel(
        name=product.name,
        slug=slug,
        description=product.description,
        price=product.price,
        sku=sku,
        stock=product.stock,
        category=product.category,
        # --- CAMBIO: Lógica de imagen simplificada ---
        # Usa el campo 'image_url' del schema y lo asigna al campo del modelo
        image_url=product.image_url,
        is_active=True,
        is_featured=False
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_data: ProductUpdate, # <-- CAMBIO: Usa el schema ProductUpdate para la entrada
    db: Session = Depends(get_db)
):
    result = await db.execute(select(ProductModel).where(ProductModel.id == product_id))
    db_product = result.scalar_one_or_none()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # --- CAMBIO: Lógica de actualización mejorada y dinámica ---
    # Convierte el schema de Pydantic a un diccionario, excluyendo los campos que no se enviaron
    update_data = product_data.dict(exclude_unset=True)

    # Itera sobre los datos enviados y actualiza el modelo de la base de datos
    for key, value in update_data.items():
        setattr(db_product, key, value)

    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(ProductModel).where(ProductModel.id == product_id))
    db_product = result.scalar_one_or_none()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    await db.delete(db_product)
    await db.commit()
    return {"message": "Producto eliminado con éxito"} # Aunque el status 204 no devuelve cuerpo, es útil para pruebas