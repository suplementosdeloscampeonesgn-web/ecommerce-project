from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
import cloudinary
import cloudinary.uploader
import pandas as pd
import os
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.product import Product
from sqlalchemy import select, update, delete
from jose import jwt

router = APIRouter()

CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

def verify_admin_token(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("is_admin"):
            raise ValueError("Not admin")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="No autorizado (admin)")

@router.get("/products")
async def get_products(
    db: AsyncSession = Depends(get_db), 
    admin=Depends(verify_admin_token)
):
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    products = result.scalars().all()
    product_list = [
        {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "price": float(p.price),
            "stock": p.stock,
            "description": p.description,
            "image": p.image_url,
            "created_at": p.created_at,
        }
        for p in products
    ]
    return {"products": product_list}

@router.post("/products")
async def create_product(
    data: dict, 
    db: AsyncSession = Depends(get_db), 
    admin=Depends(verify_admin_token)
):
    new_product = Product(**data)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return {"success": True, "product_id": new_product.id}

@router.put("/products/{product_id}")
async def update_product(
    product_id: int, 
    data: dict, 
    db: AsyncSession = Depends(get_db), 
    admin=Depends(verify_admin_token)
):
    await db.execute(update(Product).where(Product.id == product_id).values(**data))
    await db.commit()
    return {"success": True}

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int, 
    db: AsyncSession = Depends(get_db), 
    admin=Depends(verify_admin_token)
):
    await db.execute(delete(Product).where(Product.id == product_id))
    await db.commit()
    return {"success": True}

@router.post("/upload-images")
async def upload_images(
    file: UploadFile = File(...), 
    admin=Depends(verify_admin_token)
):
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        result = cloudinary.uploader.upload(
            temp_path,
            folder="campeones-gn/products",
            transformation=[
                {"width": 800, "height": 800, "crop": "limit"},
                {"quality": "auto"}
            ]
        )
        os.remove(temp_path)
        return {"urls": [result["secure_url"]]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-excel")
async def import_excel(
    excel: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db), 
    admin=Depends(verify_admin_token)
):
    try:
        df = pd.read_excel(excel.file)
        imported = 0
        for _, row in df.iterrows():
            data = dict(
                name=row.get('Nombre', ''),
                brand=row.get('Marca', ''),
                category=row.get('Categoria', ''),
                price=float(row.get('Precio', 0)),
                stock=int(row.get('Stock', 0)),
                description=row.get('Descripcion', '')
            )
            existing = await db.execute(
                select(Product).where(Product.name == data["name"], Product.brand == data["brand"])
            )
            product = existing.scalar_one_or_none()
            if product:
                await db.execute(update(Product)
                    .where(Product.id == product.id)
                    .values(**data))
            else:
                new_product = Product(**data)
                db.add(new_product)
            imported += 1
        await db.commit()
        return {"success": True, "imported": imported}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))