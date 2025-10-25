from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from pydantic import BaseModel
import cloudinary
import cloudinary.uploader
import pandas as pd
import os
import logging # Importar logging
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.product import Product
from models.order import Order, OrderItem, OrderStatus # ✅ 1. Importa el Enum
from models.user import User
from sqlalchemy import select, update, delete, func, extract, desc
from jose import jwt
from datetime import datetime, timedelta

# Configurar un logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------- CONFIG CLOUDINARY ----------------
# (Tu config de Cloudinary está bien)
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
    """
    Dependencia de FastAPI para verificar el token JWT de un administrador.
    Lee el header 'Authorization' y valida el rol.
    """
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Esquema de autorización no válido")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        is_admin_flag = payload.get("is_admin", False)
        role = payload.get("role", "")
        
        if not is_admin_flag and role.upper() != "ADMIN":
            raise ValueError("No es administrador")
            
        return payload
    except Exception as e:
        logger.error(f"Error en la validación del token: {e}")
        raise HTTPException(
            status_code=401, 
            detail=f"No autorizado (admin): {str(e)}"
        )

# ---------------- DASHBOARD ADMIN ----------------
@router.get("/dashboard")
async def dashboard_metrics(db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Obtiene las métricas clave para el dashboard del administrador.
    """
    try:
        now = datetime.utcnow()
        
        # ✅ 2. CORREGIDO: Usar los valores del Enum
        valid_income_statuses = [OrderStatus.DELIVERED, OrderStatus.SHIPPED]
        
        logger.info("Iniciando consulta de dashboard: 1. Ingresos")
        ingresos_res = await db.execute(
            select(func.sum(Order.total_amount)).where(
                extract("month", Order.created_at) == now.month,
                extract("year", Order.created_at) == now.year,
                Order.status.in_(valid_income_statuses) # ✅ Usar la variable
            )
        )
        ingresos = ingresos_res.scalar() or 0
        
        logger.info("Iniciando consulta de dashboard: 2. Pedidos del mes")
        pedidos_mes_res = await db.execute(
            select(func.count(Order.id)).where(
                extract("month", Order.created_at) == now.month,
                extract("year", Order.created_at) == now.year
            )
        )
        pedidos_mes = pedidos_mes_res.scalar() or 0
        
        logger.info("Iniciando consulta de dashboard: 3. Clientes")
        clientes_res = await db.execute(
            select(func.count(User.id)).where(
                extract("month", User.created_at) == now.month,
                extract("year", User.created_at) == now.year
            )
        )
        clientes_mes = clientes_res.scalar() or 0

        logger.info("Iniciando consulta de dashboard: 4. Ventas (7 días)")
        salesData = []
        for d in range(7, -1, -1): # Incluir hoy
            date = now - timedelta(days=d)
            ventas_res = await db.execute(
                select(func.sum(Order.total_amount)).where(
                    func.date(Order.created_at) == date.date(),
                    Order.status.in_(valid_income_statuses) # ✅ Usar la variable
                )
            )
            ventas = ventas_res.scalar() or 0
            salesData.append({"name": date.strftime("%d %b"), "ventas": ventas})

        logger.info("Iniciando consulta de dashboard: 5. Top Productos")
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

        logger.info("Iniciando consulta de dashboard: 6. Pedidos Recientes")
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

        logger.info("Consultas de dashboard completadas con éxito.")
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
        logger.exception(f"Error 500 al generar métricas del dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar métricas: {e}")

# ---------------- PRODUCTOS ADMIN ----------------
@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Obtiene la lista de todos los productos para el panel de admin.
    """
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    products = result.scalars().all()
    
    return [{
            "id": p.id, 
            "name": p.name, 
            "brand": p.brand, 
            "category": p.category,
            "price": float(p.price), 
            "stock": p.stock, 
            "description": p.description,
            "created_at": p.created_at,
            "imageUrl": p.image_url # (Esto ya estaba bien)
        } for p in products]

@router.post("/products")
async def create_product(data: dict, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Crea un nuevo producto en la base de datos.
    El frontend debe enviar 'image_url' en el 'data'.
    """
    try:
        new_product = Product(**data)
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return {"success": True, "product_id": new_product.id}
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error 400 al crear producto: {e}")
        raise HTTPException(status_code=400, detail=f"Error al crear producto: {e}")

@router.put("/products/{product_id}")
async def update_product(product_id: int, data: dict, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Actualiza un producto existente por su ID.
    """
    try:
        await db.execute(update(Product).where(Product.id == product_id).values(**data))
        await db.commit()
        return {"success": True}
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error 400 al actualizar producto: {e}")
        raise HTTPException(status_code=400, detail=f"Error al actualizar producto: {e}")

@router.delete("/products/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Elimina un producto por su ID.
    """
    try:
        await db.execute(delete(Product).where(Product.id == product_id))
        await db.commit()
        return {"success": True}
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error 500 al eliminar producto: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar producto: {e}")

# ---------------- PEDIDOS ADMIN ----------------

class StatusUpdateRequest(BaseModel):
    """Schema para validar el body del request de actualización de estado."""
    status: str

@router.get("/orders")
async def get_all_orders(
    db: AsyncSession = Depends(get_db), 
    admin = Depends(verify_admin_token)
):
    """
    Obtiene todos los pedidos con detalles de usuario e items para el panel de admin.
    """
    try:
        query = (
            select(Order, User)
            .join(User, Order.user_id == User.id)
            .order_by(desc(Order.created_at))
        )
        result = await db.execute(query)
        all_orders = result.fetchall()
        
        orders_list = []
        
        for order, user in all_orders:
            items_query = (
                select(OrderItem, Product.name.label("product_name"), Product.price.label("product_price"))
                .join(Product, OrderItem.product_id == Product.id)
                .where(OrderItem.order_id == order.id)
            )
            items_result = await db.execute(items_query)
            order_items = items_result.fetchall()
            
            orders_list.append({
                "id": order.id,
                "created_at": order.created_at,
                "total_amount": float(order.total_amount),
                "status": order.status.value if hasattr(order.status, "value") else order.status,
                "shipping_address": getattr(order, 'shipping_address_str', 'N/A'),
                "user": {
                    "name": user.name,
                    "email": user.email
                },
                "items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "product_name": product_name,
                        "product_price": float(product_price)
                    } for item, product_name, product_price in order_items
                ]
            })
        
        return orders_list
        
    except Exception as e:
        logger.exception(f"Error 500 al obtener pedidos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")

@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int, 
    request: StatusUpdateRequest, 
    db: AsyncSession = Depends(get_db), 
    admin = Depends(verify_admin_token)
):
    """
    Actualiza el estado de un pedido específico.
    """
    try:
        # ✅ 3. CORREGIDO: Usar los Enums reales
        valid_statuses = {s.value for s in OrderStatus}
        status_upper = request.status.upper()
        
        if status_upper not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Estado no válido: {request.status}")

        order_res = await db.execute(select(Order).where(Order.id == order_id))
        order = order_res.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        await db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(status=status_upper)
        )
        await db.commit()
        
        return {"success": True, "order_id": order_id, "new_status": status_upper}
        
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        logger.exception(f"Error 500 al actualizar estado: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar estado: {str(e)}")


# ---------------- UTILIDADES ADMIN (IMÁGENES & EXCEL) ----------------
@router.post("/upload-images")
async def upload_images(file: UploadFile = File(...), admin=Depends(verify_admin_token)):
    """
    Sube una imagen de producto a Cloudinary.
    """
    temp_path = f"/tmp/{file.filename}"
    try:
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
        return {"urls": [result["secure_url"]]}
    except Exception as e:
        logger.exception(f"Error 500 al subir imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")
    finally:
        if os.path.exists(temp_path):
             os.remove(temp_path)

@router.post("/import-excel")
async def import_excel(excel: UploadFile = File(...), db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Importa o actualiza productos masivamente desde un archivo Excel.
    """
    try:
        df = pd.read_excel(excel.file)
        imported_count = 0
        updated_count = 0

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
                updated_count += 1
            else:
                new_product = Product(**data)
                db.add(new_product)
                imported_count += 1

        await db.commit()
        return {"success": True, "imported": imported_count, "updated": updated_count}
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error 500 al importar Excel: {e}")
        raise HTTPException(status_code=500, detail=f"Error al importar Excel: {e}")