# backend/core/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, parse_qs, urlunparse
from core.config import settings


# --- Conexión a la Base de Datos ---

# 1. Obtenemos la URL desde la configuración (.env -> DATABASE_URL)
db_url = settings.DATABASE_URL
parsed_url = urlparse(db_url)
query_params = parse_qs(parsed_url.query)

# 2. Preparamos los argumentos de conexión
connect_args = {}
if "sslmode" in query_params:
    connect_args["ssl"] = query_params["sslmode"][0]
elif "ssl" not in connect_args:
    connect_args["ssl"] = "require"  # asegúrate de SSL para NeonDB

# 3. Reconstruimos la URL sin los parámetros que ahora van en connect_args
base_url = urlunparse(parsed_url._replace(query=""))
if base_url.endswith("?"):
    base_url = base_url[:-1]

# 4. Log de depuración
print("=" * 80)
print("ATENCIÓN: La aplicación se está conectando con la siguiente configuración:")
print(f"URL Base: {base_url}")
print(f"Argumentos de conexión: {connect_args}")
print("=" * 80)

# 5. Motor SQLAlchemy (optimizado para NeonDB)
async_engine = create_async_engine(
    base_url.replace("postgresql://", "postgresql+asyncpg://"),
    connect_args=connect_args,
    pool_size=5,             # conexiones estables mínimas
    max_overflow=10,         # conexiones extra si el pool se llena
    pool_recycle=180,        # recicla conexiones cada 3 minutos
    pool_timeout=30,         # espera antes de lanzar error de pool lleno
    echo=False               # cambia a True para debug SQL
)

# --- Configuración de la sesión ---
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()


# --- Dependencia de Sesión ---
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# --- Creación de Tablas ---
async def create_tables():
    from models.product import Product
    from models.user import User
    from models.order import Order, OrderItem

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
