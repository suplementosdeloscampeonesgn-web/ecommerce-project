from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging # <-- Añadir logging para ver inicio

from core.config import settings
from core.database import create_tables
from api import auth, products, cart, orders, admin, address 

# Configurar logger
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación y creando tablas si no existen...")
    await create_tables()
    logger.info("El proceso de creación de tablas ha finalizado.")
    yield
    logger.info("Cerrando aplicación.")

app = FastAPI(
    title="E-commerce API",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- CONFIGURACIÓN DE CORS ---
origins = [
    "https://www.suplementosdeloscampeonesgn.shop",
    "https://suplementosdeloscampeonesgn.shop",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTRO DE RUTAS ---
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# ✅ CORRECCIÓN: Añadir la barra inclinada al final del prefijo
app.include_router(products.router, prefix="/api/products/", tags=["products"]) 

# (Recomendado añadir slash también a los otros para consistencia)
app.include_router(cart.router, prefix="/api/cart/", tags=["cart"]) 
app.include_router(orders.router, prefix="/api/orders/", tags=["orders"]) 
app.include_router(address.router, prefix="/api/address/", tags=["address"]) 
app.include_router(admin.router, prefix="/api/admin/", tags=["admin"]) 

@app.get("/")
async def root():
    return {"message": "E-commerce API funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)