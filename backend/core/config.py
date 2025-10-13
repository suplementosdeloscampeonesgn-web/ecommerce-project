# en backend/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Variables que ya tenías
    DATABASE_URL: str
    SECRET_KEY: str
    
    # Estas pueden tener un valor por defecto si quieres
    ALGORITHM: str = "HS256"
    FRONTEND_URL: str

    # --- Variables de entorno que añadimos ---
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    FROM_EMAIL: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()