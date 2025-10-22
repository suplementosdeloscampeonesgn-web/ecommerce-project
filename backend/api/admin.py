from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
import cloudinary
import cloudinary.uploader
import pandas as pd
import os
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.product import Product
from models.order import Order, OrderItem
from models.user import User
from sqlalchemy import select, update, delete, func, extract, desc
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

# ---------------- CONFIG CLOUDINARY ----------------
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

# ---------------- VALIDACIÓN ADMIN ----------------
def verify_admin_token(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("is_admin") and payload.get("role") != "admin":
            raise ValueError("Not admin")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="No autorizado (admin)")

# ---------------- DASHBOARD ADMIN ----------------
@router.get("/dashboard")
async def dashboard_metrics(db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    try:
        now = datetime.utcnow()

        # Ingresos mensuales
        ingresos_res = await db.execute(
            select(func.sum(Order.total_amount)).where(
                extract("month", Order.created_at) == now.month,
                extract("year", Order.created_at) == now.year,
                Order.status.in_(["delivered", "shipped"])
            )
        )
        ingresos = ingresos_res.scalar() or 0

        # Nuevos pedidos este mes
        pedidos_mes_res = await db.execute(
            select(func.count(Order.id)).where(
                extract("month", Order.created_at) == now.month,
                extract("year", Order.created_at) == now.year
            )
        )
        pedidos_mes = pedidos_mes_res.scalar() or 0

        # Nuevos clientes este mes
        clientes_res = await db.execute(
            select(func.count(User.id)).where(
                extract("month", User.created_at) == now.month,
                extract("year", User.created_at) == now.year
            )
        )
        clientes_mes = clientes_res.scalar() or 0

        # Ventas diarias para la gráfica
        salesData = []
        for d in range(7, 0, -1):
            date = now - timedelta(days=d)
            ventas_res = await db.execute(
                select(func.sum(Order.total_amount)).where(
                    func.date(Order.created_at) == date.date(),
                    Order.status.in_(["delivered", "shipped"])
                )
            )
            ventas = ventas_res.scalar() or 0
            salesData.append({
                "name": date.strftime("%d %b"),
                "ventas": ventas
            })

        # Top productos más vendidos
        top_query = (
            select(OrderItem.product_id, Product.name, func.sum(OrderItem.quantity).label("sold"))
            .join(Product, Product.id == OrderItem.product_id)
            .group_by(OrderItem.product_id, Product.name)
            .order_by(desc("sold"))
            .limit(5)
        )
        top_result = await db.execute(top_query)
        topProducts = [
            {"id": r.product_id, "name": r.name, "sold": r.sold}
            for r in top_result.fetchall()
        ]

        # Pedidos recientes
        recent_query = (
            select(Order, User)
            .join(User, Order.user_id == User.id)
            .order_by(desc(Order.created_at))
            .limit(5)
        )
        recent_result = await db.execute(recent_query)
        recentOrders = [{
            "id": order.id,
            "customer": user.name if hasattr(user, "name") else "Cliente",
            "date": order.created_at.strftime("%b %d, %Y"),
            "total": float(order.total_amount),
            "status": order.status.value if hasattr(order.status, "value") else order.status
        } for order, user in recent_result.fetchall()]

        return {
            "stats": [
                {"title": "Ingresos (Mes)", "value": f"${ingresos:,.2f}"},
                {"title": "Nuevos Pedidos", "value": pedidos_mes},
                {"title": "Nuevos Clientes", "value": clientes_mes}
            ],
            "salesData": salesData,
            "topProducts": topProducts,
            "recentOrders": recentOrders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar métricas: {e}")

# ---------------- PRODUCTOS ADMIN ----------------
@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    products = result.scalars().all()
    return {
        "products": [{
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "price": float(p.price),
            "stock": p.stock,
            "description": p.description,
            "image": p.image_url,
            "created_at": p.created_at
        } for p in products]
    }

@router.post("/products")
async def create_product(data: dict, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    new_product = Product(**data)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return {"success": True, "product_id": new_product.id}

@router.put("/products/{product_id}")
async def update_product(product_id: int, data: dict, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    await db.execute(update(Product).where(Product.id == product_id).values(**data))
    await db.commit()
    return {"success": True}

@router.delete("/products/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    await db.execute(delete(Product).where(Product.id == product_id))
    await db.commit()
    return {"success": True}

# ---------------- SUBIDA DE IMÁGENES ----------------
@router.post("/upload-images")
async def upload_images(file: UploadFile = File(...), admin=Depends(verify_admin_token)):
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
            ],
        )
        os.remove(temp_path)
        return {"urls": [result["secure_url"]]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")

# ---------------- IMPORTACIÓN EXCEL ----------------
@router.post("/import-excel")
async def import_excel(excel: UploadFile = File(...), db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    try:
        df = pd.read_excel(excel.file)
        imported = 0

        for _, row in df.iterrows():
            data = dict(
                name=row.get("Nombre", ""),
                brand=row.get("Marca", ""),
                category=row.get("Categoria", ""),
                price=float(row.get("Precio", 0)),
                stock=int(row.get("Stock", 0)),
                description=row.get("Descripcion", "")
            )
            existing = await db.execute(select(Product).where(Product.name == data["name"], Product.brand == data["brand"]))
            product = existing.scalar_one_or_none()

            if product:
                await db.execute(update(Product).where(Product.id == product.id).values(**data))
            else:
                new_product = Product(**data)
                db.add(new_product)
            imported += 1

        await db.commit()
        return {"success": True, "imported": imported}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al importar Excel: {e}")
