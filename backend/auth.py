from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

# Llave secreta para firmar los tokens (en un proyecto real esto va en un archivo oculto .env)
SECRET_KEY = "fiusac_super_secreta_llave_iot_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # El administrador será deslogueado automáticamente en 1 hora por seguridad

# Configuramos Bcrypt, el algoritmo de encriptación estándar de la industria
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import hashlib

# Función para comparar contraseñas
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or not plain_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback de compatibilidad si el valor histórico aún no era un hash bcrypt válido
        return plain_password == hashed_password

# Función para hashear contraseñas nuevas
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Funciones para la llave temporal de recuperación del Admin
def hash_recovery_key(key: str) -> str:
    if not key:
        return ""
    return hashlib.sha256(key.strip().upper().encode("utf-8")).hexdigest()

def verify_recovery_key(plain_key: str, hashed_key: str) -> bool:
    if not plain_key or not hashed_key:
        return False
    return hash_recovery_key(plain_key) == hashed_key

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

security = HTTPBearer(auto_error=False)

# Función para generar la "llave digital" (Token) cuando el Admin inicia sesión
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Creamos el Token firmado con nuestra llave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencia para proteger endpoints administrativos
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso no autorizado. Se requiere un Token JWT de Administrador válido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
