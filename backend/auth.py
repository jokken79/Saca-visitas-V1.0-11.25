# ============================================================
# UNS VISA SYSTEM - Authentication Module
# JWT Authentication with roles
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import os

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ============================================================
# MODELS
# ============================================================

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "staff"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    last_login: Optional[datetime]

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash de password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """Decodificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="トークンが無効です",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, user_id=user_id, role=role)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの有効期限が切れています",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンが無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Obtener usuario actual desde token"""
    return decode_token(token)

async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Verificar que el usuario esté activo"""
    # Aquí podrías verificar en la base de datos si el usuario está activo
    return current_user

def require_role(allowed_roles: list):
    """Decorator para requerir roles específicos"""
    async def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="この操作を行う権限がありません"
            )
        return current_user
    return role_checker

# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    ログイン - Login
    
    Autenticar usuario y devolver token JWT
    """
    # Aquí deberías buscar el usuario en la base de datos
    # Por ahora, simulamos con un usuario de ejemplo
    
    # Simular búsqueda en DB
    fake_users_db = {
        "admin": {
            "id": 1,
            "username": "admin",
            "email": "admin@uns-visa.jp",
            "full_name": "System Administrator",
            "hashed_password": get_password_hash("admin123"),
            "role": "admin",
            "is_active": True
        },
        "staff": {
            "id": 2,
            "username": "staff",
            "email": "staff@uns-visa.jp",
            "full_name": "Staff User",
            "hashed_password": get_password_hash("staff123"),
            "role": "staff",
            "is_active": True
        }
    }
    
    user = fake_users_db.get(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="アカウントが無効です"
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "user_id": user["id"],
            "role": user["role"]
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    }

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """
    現在のユーザー情報 - Current user info
    """
    return {
        "username": current_user.username,
        "user_id": current_user.user_id,
        "role": current_user.role
    }

@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    ログアウト - Logout
    
    En JWT stateless, el logout se maneja en el cliente
    eliminando el token almacenado
    """
    return {
        "message": "ログアウトしました",
        "detail": "トークンをクライアント側で削除してください"
    }

@router.post("/refresh")
async def refresh_token(current_user: TokenData = Depends(get_current_user)):
    """
    トークン更新 - Refresh token
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": current_user.username,
            "user_id": current_user.user_id,
            "role": current_user.role
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: TokenData = Depends(get_current_user)
):
    """
    パスワード変更 - Change password
    """
    # Aquí verificarías el password actual en la DB
    # y actualizarías con el nuevo
    
    return {
        "message": "パスワードが変更されました"
    }

# ============================================================
# ADMIN ONLY ENDPOINTS
# ============================================================

@router.post("/users", dependencies=[Depends(require_role(["admin"]))])
async def create_user(user: UserCreate):
    """
    ユーザー作成 - Create user (Admin only)
    """
    hashed_password = get_password_hash(user.password)
    
    # Aquí insertarías en la base de datos
    
    return {
        "message": "ユーザーが作成されました",
        "username": user.username
    }

@router.get("/users", dependencies=[Depends(require_role(["admin"]))])
async def list_users():
    """
    ユーザー一覧 - List users (Admin only)
    """
    # Aquí consultarías la base de datos
    
    return [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@uns-visa.jp",
            "full_name": "System Administrator",
            "role": "admin",
            "is_active": True
        }
    ]

@router.delete("/users/{user_id}", dependencies=[Depends(require_role(["admin"]))])
async def delete_user(user_id: int):
    """
    ユーザー削除 - Delete user (Admin only)
    """
    return {"message": f"ユーザー {user_id} が削除されました"}
