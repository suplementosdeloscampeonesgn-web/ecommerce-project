from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles # <- Comentado para Serverless
from contextlib import asynccontextmanager
import logging

from core.config import settings
from core.database import create_tables
from api import auth, products, cart, orders, admin, address 

# Configurar logger
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # En Serverless (Vercel), es mejor evitar crear tablas en cada arranque.
    # Descomenta la siguiente línea solo si necesitas forzar la creación de tablas,
    # pero es mejor hacerlo mediante migraciones (Alembic) o un script local.
    
    # await create_tables() 
    
    logger.info("API iniciada en entorno Serverless.")
    yield
    logger.info("Cerrando instancia de la API.")

app = FastAPI(
    title="E-commerce API",
    version="1.0.0",
    lifespan=lifespan
)

# app.mount("/static", StaticFiles(directory="static"), name="static") # <- Comentado para Serverless

# --- CONFIGURACIÓN DE CORS ---
# Vercel asignará URLs dinámicas. Aseguramos que los orígenes estén bien cubiertos.
origins = [
    "https://www.suplementosdeloscampeonesgn.shop",
    "https://suplementosdeloscampeonesgn.shop",
    "http://localhost:5173",
    "http://localhost:3000"
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
app.include_router(products.router, prefix="/api/products", tags=["products"]) 
app.include_router(cart.router, prefix="/api/cart", tags=["cart"]) 
app.include_router(orders.router, prefix="/api/orders", tags=["orders"]) 
app.include_router(address.router, prefix="/api/address", tags=["address"]) 
app.include_router(admin.router, prefix="/api/admin", tags=["admin"]) 

@app.get("/")
async def root():
    return {
        "message": "E-commerce API funcionando en Vercel 🚀",
        "status": "Online"
    }

# El bloque de uvicorn se ignora en Vercel, pero se deja para pruebas locales
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)