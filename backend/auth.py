from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

# Llave secreta para firmar los tokens (en un proyecto real esto va en un archivo oculto .env)
SECRET_KEY = "fiusac_super_secreta_llave_iot_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # El administrador será deslogueado automáticamente en 1 hora por seguridad

# Configuramos Bcrypt, el algoritmo de encriptación estándar de la industria
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para comparar contraseñas
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para encriptar contraseñas nuevas
def get_password_hash(password):
    return pwd_context.hash(password)

# Función para generar la "llave digital" (Token) cuando el Admin inicia sesión
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Creamos el Token firmado con nuestra llave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
