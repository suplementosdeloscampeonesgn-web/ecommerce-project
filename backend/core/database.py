# en backend/core/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, parse_qs, urlunparse
from core.config import settings

# --- Conexión a la Base de Datos ---

# 1. Obtenemos la URL desde la configuración
db_url = settings.DATABASE_URL
parsed_url = urlparse(db_url)
query_params = parse_qs(parsed_url.query)

# 2. Preparamos los argumentos de conexión
connect_args = {}
if 'sslmode' in query_params:
    connect_args['ssl'] = query_params['sslmode'][0]

# 3. Reconstruimos la URL sin los parámetros que ahora van en connect_args
# Esto evita que 'sslmode' o 'channel_binding' confundan al driver
base_url = urlunparse(parsed_url._replace(query=""))
# Eliminamos el '?' si la URL base termina con él
if base_url.endswith('?'):
    base_url = base_url[:-1]

# 4. Imprimimos para depuración
print("=" * 80)
print(f"ATENCIÓN: La aplicación se está conectando con la siguiente configuración:")
print(f"URL Base: {base_url}")
print(f"Argumentos de conexión: {connect_args}")
print("=" * 80)

# 5. Creamos el motor, pasando la URL y los argumentos de conexión
async_engine = create_async_engine(
    base_url.replace("postgresql://", "postgresql+asyncpg://"),
    connect_args=connect_args
)

# --- Configuración de la Sesión ---
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

# --- Funciones de Dependencia y Creación de Tablas ---
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    from models.product import Product
    from models.user import User
    from models.order import Order, OrderItem
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)