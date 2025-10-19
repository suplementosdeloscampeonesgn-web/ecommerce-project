from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import create_tables
from api import auth, products, cart, orders, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación y creando tablas...")
    await create_tables()
    print("El proceso de creación de tablas ha finalizado.")
    yield
    print("Cerrando aplicación.")

app = FastAPI(
    title="E-commerce API",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- CONFIGURACIÓN DE CORS PARA PRODUCCIÓN ---
# ✅ Se especifican los dominios permitidos.
origins = [
    "https://www.suplementosdeloscampeonesgn.shop", # Tu dominio de producción
    "http://localhost:5173",                 # Tu dominio de desarrollo local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "E-commerce API funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)