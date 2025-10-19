from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import create_tables
# Se importan todos los routers, incluyendo el nuevo de categorías
from api import auth, products, cart, orders, admin, categories

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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSIÓN DE RUTAS MODULARES ---
# Cada parte de la API tiene su propio prefijo y archivo.
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
# ✅ Se incluye el nuevo router para las categorías
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])


@app.get("/")
async def root():
    return {"message": "E-commerce API funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)