from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cloudinary
import cloudinary.uploader
import pandas as pd
import os
import logging
import io # Para exportar a Excel
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.product import Product
from models.order import Order, OrderItem, OrderStatus # ✅ Importa el Enum
from models.user import User, UserRole # ✅ Importa UserRole
from sqlalchemy import select, update, delete, func, extract, desc
from sqlalchemy.orm import joinedload, selectinload
from jose import jwt
from datetime import datetime, timedelta

# Configurar un logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# ---------------- SCHEMAS (BUENA PRÁCTICA) ----------------

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    # Asumo que tienes 'brand' en tu modelo Product según tu código original
    brand: Optional[str] = None 
    slug: Optional[str] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

class StatusUpdateRequest(BaseModel):
    status: str

class UserRoleUpdate(BaseModel):
    role: UserRole # Usa el Enum para validación automática

# ---------------- VALIDACIÓN ADMIN (OK) ----------------
def verify_admin_token(authorization: str = Header(...)):
    """
    Dependencia de FastAPI para verificar el token JWT de un administrador.
    """
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Esquema de autorización no válido")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        is_admin_flag = payload.get("is_admin", False)
        role = payload.get("role", "")
        
        # Comprueba ambos flags por si acaso
        if not is_admin_flag and role.upper() != "ADMIN":
            raise ValueError("No es administrador")
            
        return payload
    except Exception as e:
        logger.error(f"Error en la validación del token: {e}")
        raise HTTPException(
            status_code=401, 
            detail=f"No autorizado (admin): {str(e)}"
        )

# ---------------- DASHBOARD ADMIN (MEJORADO) ----------------
@router.get("/dashboard")
async def dashboard_metrics(db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Obtiene las métricas clave para el dashboard del administrador.
    """
    try:
        now = datetime.utcnow()
        
        # ✅ ¡CORREGIDO! Usar los valores en español del Enum
        valid_income_statuses = [OrderStatus.COMPLETADO, OrderStatus.ENVIADO]
        
        # --- 1. KPIs Principales (Stats) ---
        logger.info("Iniciando consulta de dashboard: 1. Ingresos (Mes)")
        ingresos_res = await db.execute(
            select(func.sum(Order.total_amount)).where(
                extract("month", Order.created_at) == now.month,
                extract("year", Order.created_at) == now.year,
                Order.status.in_(valid_income_statuses)
            )
        )
        ingresos_mes = ingresos_res.scalar() or 0
        
        logger.info("Iniciando consulta de dashboard: 2. Pedidos (Mes)")
        pedidos_mes_res = await db.execute(
            select(func.count(Order.id)).where(
                extract("month", Order.created_at) == now.month,
                extract("year", Order.created_at) == now.year
            )
        )
        pedidos_mes = pedidos_mes_res.scalar() or 0
        
        logger.info("Iniciando consulta de dashboard: 3. Clientes (Mes)")
        clientes_mes_res = await db.execute(
            select(func.count(User.id)).where(
                extract("month", User.created_at) == now.month,
                extract("year", User.created_at) == now.year
            )
        )
        clientes_mes = clientes_mes_res.scalar() or 0

        # --- 2. KPIs Globales (NUEVO) ---
        logger.info("Iniciando consulta de dashboard: 4. KPIs Globales")
        total_users_res = await db.execute(select(func.count(User.id)))
        total_users = total_users_res.scalar() or 0
        
        total_products_res = await db.execute(select(func.count(Product.id)))
        total_products = total_products_res.scalar() or 0
        
        total_orders_res = await db.execute(select(func.count(Order.id)))
        total_orders = total_orders_res.scalar() or 0
        
        aov_res = await db.execute(
            select(func.avg(Order.total_amount)).where(Order.status.in_(valid_income_statuses))
        )
        average_order_value = aov_res.scalar() or 0

        # --- 3. Gráfica de Ventas (7 días) ---
        logger.info("Iniciando consulta de dashboard: 5. Ventas (7 días)")
        salesData = []
        for d in range(6, -1, -1): # 7 días incluyendo hoy
            date = now - timedelta(days=d)
            ventas_res = await db.execute(
                select(func.sum(Order.total_amount)).where(
                    func.date(Order.created_at) == date.date(),
                    Order.status.in_(valid_income_statuses)
                )
            )
            ventas = ventas_res.scalar() or 0
            salesData.append({"name": date.strftime("%d %b"), "ventas": round(ventas, 2)})

        # --- 4. Top Productos (OK) ---
        logger.info("Iniciando consulta de dashboard: 6. Top Productos")
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

        # --- 5. Pedidos Recientes (OK) ---
        logger.info("Iniciando consulta de dashboard: 7. Pedidos Recientes")
        recent_query = (
            select(Order, User)
            .join(User, Order.user_id == User.id)
            .order_by(desc(Order.created_at))
            .limit(5)
        )
        recent_result = await db.execute(recent_query)
        recentOrders = [{
            "id": order.id,
            "customer": user.name,
            "date": order.created_at.strftime("%b %d, %Y"),
            "total": float(order.total_amount),
            "status": order.status.value
        } for order, user in recent_result.fetchall()]

        # --- 6. Desglose de Estados (NUEVO) ---
        logger.info("Iniciando consulta de dashboard: 8. Desglose de Estados")
        status_query = select(Order.status, func.count(Order.id).label("count")).group_by(Order.status)
        status_result = await db.execute(status_query)
        statusBreakdown = [
            {"name": status.value, "value": count}
            for status, count in status_result.fetchall()
        ]

        logger.info("Consultas de dashboard completadas con éxito.")
        return {
            "stats": [
                {"title": "Ingresos (Mes)", "value": f"${ingresos_mes:,.2f}"},
                {"title": "Nuevos Pedidos (Mes)", "value": pedidos_mes},
                {"title": "Nuevos Clientes (Mes)", "value": clientes_mes},
                {"title": "Ticket Promedio (AOV)", "value": f"${average_order_value:,.2f}"}
            ],
            "kpis": {
                "total_users": total_users,
                "total_products": total_products,
                "total_orders": total_orders
            },
            "salesData": salesData,
            "topProducts": topProducts,
            "recentOrders": recentOrders,
            "statusBreakdown": statusBreakdown
        }
    except Exception as e:
        logger.exception(f"Error 500 al generar métricas del dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar métricas: {e}")

# ---------------- PRODUCTOS ADMIN (MEJORADO CON SCHEMAS) ----------------
@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Obtiene la lista de todos los productos para el panel de admin.
    """
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    products = result.scalars().all()
    
    # Devuelve la lista completa de productos
    return products

@router.post("/products")
async def create_product(product_data: ProductCreate, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Crea un nuevo producto usando un schema Pydantic para validación.
    """
    try:
        # Crea el slug si no se provee
        if not product_data.slug:
            product_data.slug = product_data.name.lower().replace(" ", "-")
        
        # Crea el SKU si no se provee
        if not product_data.sku:
            product_data.sku = f"{product_data.brand[:3].upper()}-{product_data.name[:3].upper()}-{product_data.price}"

        new_product = Product(**product_data.model_dump())
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return {"success": True, "product_id": new_product.id}
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error 400 al crear producto: {e}")
        raise HTTPException(status_code=400, detail=f"Error al crear producto: {e}")

@router.put("/products/{product_id}")
async def update_product(product_id: int, product_data: ProductUpdate, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    """
    Actualiza un producto existente por su ID usando un schema Pydantic.
    """
    try:
        # Convierte el schema a dict, excluyendo valores no seteados
        update_data = product_data.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")

        await db.execute(update(Product).where(Product.id == product_id).values(**update_data))
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

# ---------------- PEDIDOS ADMIN (OPTIMIZADO N+1) ----------------

@router.get("/orders")
async def get_all_orders(
    db: AsyncSession = Depends(get_db), 
    admin = Depends(verify_admin_token)
):
    """
    Obtiene todos los pedidos con detalles de usuario e items (Optimizado).
    """
    try:
        # 1. Obtener todos los pedidos con la info del usuario (joinedload)
        order_query = (
            select(Order)
            .options(joinedload(Order.user))
            .order_by(desc(Order.created_at))
        )
        order_result = await db.execute(order_query)
        orders = order_result.scalars().unique().all()
        
        order_ids = [order.id for order in orders]
        
        if not order_ids:
            return []
            
        # 2. Obtener TODOS los items y productos para esos pedidos en UNA consulta
        items_query = (
            select(OrderItem)
            .options(joinedload(OrderItem.product)) # Carga el producto de cada item
            .where(OrderItem.order_id.in_(order_ids))
        )
        items_result = await db.execute(items_query)
        all_items = items_result.scalars().all()
        
        # 3. Mapear los items a sus pedidos en Python (mucho más rápido)
        items_by_order_id = {}
        for item in all_items:
            if item.order_id not in items_by_order_id:
                items_by_order_id[item.order_id] = []
            items_by_order_id[item.order_id].append({
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product_name": item.product.name if item.product else "Producto Eliminado",
                "product_price": float(item.product.price) if item.product else 0.0
            })
            
        # 4. Construir la respuesta final
        orders_list = []
        for order in orders:
            orders_list.append({
                "id": order.id,
                "created_at": order.created_at,
                "total_amount": float(order.total_amount),
                "status": order.status.value,
                "shipping_address": order.shipping_address,
                "user": {
                    "name": order.user.name,
                    "email": order.user.email
                },
                "items": items_by_order_id.get(order.id, []) # Asigna los items desde el mapa
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
    (Esta función ya estaba bien escrita y robusta).
    """
    try:
        # Valida que el string de estado exista en los valores del Enum
        valid_statuses = {s.value for s in OrderStatus}
        status_upper = request.status.upper()
        
        if status_upper not in valid_statuses:
            logger.warning(f"Intento de actualizar a estado no válido: {request.status}")
            raise HTTPException(status_code=400, detail=f"Estado no válido: {request.status}")

        order_res = await db.execute(select(Order).where(Order.id == order_id))
        order = order_res.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Actualiza el estado usando el valor de string validado
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


# ---------------- GESTIÓN DE USUARIOS (NUEVO) ----------------

@router.get("/users")
async def get_all_users(
    db: AsyncSession = Depends(get_db), 
    admin = Depends(verify_admin_token)
):
    """
    Obtiene una lista de todos los usuarios.
    """
    try:
        result = await db.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.exception(f"Error al obtener usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener usuarios")

@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: int, 
    request: UserRoleUpdate,
    db: AsyncSession = Depends(get_db), 
    admin = Depends(verify_admin_token)
):
    """
    Actualiza el rol de un usuario (ej. a ADMIN o USER).
    """
    try:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(role=request.role) # Pydantic ya validó el Enum
        )
        await db.commit()
        return {"success": True, "user_id": user_id, "new_role": request.role.value}
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error al actualizar rol de usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar rol")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    admin = Depends(verify_admin_token)
):
    """
    Elimina un usuario (Ban). 
    ADVERTENCIA: Esto puede causar errores si no se maneja 'on_delete=CASCADE' en las FKs.
    Una mejor alternativa es 'is_active = False'.
    """
    try:
        # Opción 1: Desactivar (Recomendado)
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        
        # Opción 2: Eliminar (Peligroso si hay pedidos)
        # await db.execute(delete(User).where(User.id == user_id))
        
        await db.commit()
        return {"success": True, "action": "user deactivated"}
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error al eliminar/desactivar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar usuario")


# ---------------- UTILIDADES ADMIN (EXCEL & IMÁGENES) ----------------
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
            # Limpia los datos de pandas (ej. NaN -> None)
            row_data = row.to_dict()
            data = {
                "name": row_data.get("Nombre"),
                "brand": row_data.get("Marca"),
                "category": row_data.get("Categoria"),
                "price": float(row_data.get("Precio", 0)),
                "stock": int(row_data.get("Stock", 0)),
                "description": row_data.get("Descripcion"),
                "slug": row_data.get("Slug"),
                "sku": row_data.get("SKU"),
                "image_url": row_data.get("Image URL")
            }
            # Filtra valores nulos para no sobrescribir con None
            data = {k: v for k, v in data.items() if pd.notna(v)}

            if not data.get("name") or not data.get("brand"):
                logger.warning(f"Omitiendo fila por falta de Nombre o Marca: {row_data}")
                continue

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


@router.get("/export-orders")
async def export_orders_to_excel(
    db: AsyncSession = Depends(get_db), 
    admin = Depends(verify_admin_token)
):
    """
    Exporta un reporte de todos los pedidos a un archivo Excel.
    Un pedido con 3 items ocupará 3 filas en el Excel.
    """
    try:
        # Usamos la misma lógica optimizada de get_all_orders
        query = (
            select(Order)
            .options(
                joinedload(Order.user),
                selectinload(Order.items).joinedload(OrderItem.product) # Carga items y sus productos
            )
            .order_by(desc(Order.created_at))
        )
        result = await db.execute(query)
        orders = result.scalars().unique().all()
        
        data_to_export = []
        
        for order in orders:
            if not order.items:
                # Incluir pedidos sin items (ej. pedidos fallidos)
                data_to_export.append({
                    "ID Pedido": order.id,
                    "Fecha": order.created_at.strftime("%Y-%m-%d %H:%M"),
                    "Cliente": order.user.name,
                    "Email Cliente": order.user.email,
                    "Total Pedido": float(order.total_amount),
                    "Estado": order.status.value,
                    "Dirección": order.shipping_address,
                    "Producto SKU": "N/A",
                    "Producto Nombre": "N/A",
                    "Cantidad": 0,
                    "Precio Unitario": 0
                })
            else:
                # Crear una fila por cada item en el pedido
                for item in order.items:
                    data_to_export.append({
                        "ID Pedido": order.id,
                        "Fecha": order.created_at.strftime("%Y-%m-%d %H:%M"),
                        "Cliente": order.user.name,
                        "Email Cliente": order.user.email,
                        "Total Pedido": float(order.total_amount),
                        "Estado": order.status.value,
                        "Dirección": order.shipping_address,
                        "Producto SKU": item.product.sku if item.product else "N/A",
                        "Producto Nombre": item.product.name if item.product else "Producto Eliminado",
                        "Cantidad": item.quantity,
                        "Precio Unitario": float(item.product.price) if item.product else 0.0
                    })
        
        if not data_to_export:
            raise HTTPException(status_code=404, detail="No hay pedidos para exportar")
            
        # Crear el DataFrame y el archivo Excel en memoria
        df = pd.DataFrame(data_to_export)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Pedidos', index=False)
        
        buffer.seek(0)
        
        # Generar nombre de archivo con fecha
        filename = f"Reporte_Pedidos_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.exception(f"Error 500 al exportar pedidos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al exportar pedidos: {str(e)}")