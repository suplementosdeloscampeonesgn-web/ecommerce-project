from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
import os

from core.database import get_db
from core.security import create_access_token, verify_google_token, hash_password, verify_password
from models.user import User, UserRole, AuthProvider


router = APIRouter()

# --- CONFIGURACIÓN ---
ADMIN_EMAIL = "suplementosdeloscampeonesgn@gmail.com"
ADMIN_PASSWORD = "ScampGn19"
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- SCHEMAS ---
class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    token_id: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

# --- LOGIN USUARIO / ADMIN ---
@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # --- LOGIN ADMIN ---
    if data.email == ADMIN_EMAIL and data.password == ADMIN_PASSWORD:
        token = create_access_token({"sub": data.email, "role": "ADMIN", "is_admin": True})
        return {
            "access_token": token,
            "role": "ADMIN",
            "email": data.email
        }

    # --- LOGIN USUARIO NORMAL ---
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    token = create_access_token({
        "sub": user.email,
        "role": user.role.value,
        "name": user.name,
        "is_admin": user.role.value == "ADMIN"
    })

    return {
        "access_token": token,
        "role": user.role.value,
        "email": user.email
    }

# --- LOGIN CON GOOGLE ---
@router.post("/google-login")
async def google_login(data: GoogleLoginRequest):
    userinfo = verify_google_token(data.token_id)
    if not userinfo:
        raise HTTPException(status_code=401, detail="Token Google inválido o email no verificado")

    token = create_access_token({
        "sub": userinfo["email"],
        "google_id": userinfo["sub"],
        "role": "USER",
        "is_admin": False
    })

    return {
        "access_token": token,
        "role": "USER",
        "email": userinfo["email"]
    }

# --- REGISTRO DE NUEVOS USUARIOS ---
@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    new_user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
        provider=AuthProvider.EMAIL,
        role=UserRole.USER,
        is_active=True
    )
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo registrar el usuario")

    token = create_access_token({
        "sub": new_user.email,
        "role": new_user.role.value,
        "name": new_user.name,
        "is_admin": False
    })

    return {
        "access_token": token,
        "role": new_user.role.value,
        "email": new_user.email
    }

# --- VERIFICAR AUTENTICACIÓN ---
@router.get("/status")
async def auth_status():
    return {"authenticated": False, "user": None}

# --- FUNCIÓN GLOBAL DE AUTENTICACIÓN ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user
