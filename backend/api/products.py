from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, delete 
import uuid
import logging

from models.product import Product as ProductModel 
from schemas.product import ProductCreate, ProductUpdate, Product as ProductSchema
from core.database import get_db 

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Products"]
)

@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    """Obtiene todos los productos activos, ordenados por nombre."""
    try:
        query = select(ProductModel).where(ProductModel.is_active == True).order_by(ProductModel.name)
        result = await db.execute(query) 
        products = result.scalars().all()
        print("### DEBUG FastAPI: productos encontrados =", len(products))  # <<-- DEPURACIÓN
        return products
    except Exception as e:
        logger.exception(f"Error al obtener todos los productos: {e}")
        raise HTTPException(status_code=500, detail="Error interno al obtener productos")

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un producto específico por su ID."""
    try:
        result = await db.execute(select(ProductModel).where(ProductModel.id == product_id)) 
        product = result.scalar_one_or_one()
        if product is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al obtener el producto {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al obtener el producto")

@router.post("/", response_model=ProductSchema, status_code=201, summary="Crea un nuevo producto (¡Proteger!)") 
async def create_product(
    product: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Crea un nuevo producto. ADVERTENCIA: Endpoint no protegido por defecto."""
    try:
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
            image_url=product.image_url,
            is_active=True,
            is_featured=False
        )
        db.add(db_product)
        await db.commit() 
        await db.refresh(db_product) 
        return db_product
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error al crear producto: {e}")
        raise HTTPException(status_code=400, detail=f"Error al crear producto: {e}")

@router.put("/{product_id}", response_model=ProductSchema, summary="Actualiza un producto (¡Proteger!)")
async def update_product(
    product_id: int,
    product_data: ProductUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Actualiza un producto existente. ADVERTENCIA: Endpoint no protegido por defecto."""
    try:
        result = await db.execute(select(ProductModel).where(ProductModel.id == product_id)) 
        db_product = result.scalar_one_or_none()
        if not db_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        update_data = product_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        await db.commit() 
        await db.refresh(db_product) 
        return db_product
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error al actualizar producto {product_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Error al actualizar producto: {e}")

@router.delete("/{product_id}", status_code=204, summary="Elimina un producto (¡Proteger!)")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)): 
    """Elimina un producto. ADVERTENCIA: Endpoint no protegido por defecto."""
    try:
        result = await db.execute(select(ProductModel).where(ProductModel.id == product_id)) 
        db_product = result.scalar_one_or_none()
        if not db_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        await db.delete(db_product)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error al eliminar producto {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar producto: {e}")
