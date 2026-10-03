from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# --- SCHEMAS PARA SOLICITUDES (AccessRequest) ---

# Esto es lo que React nos va a enviar cuando alguien llene el formulario
class AccessRequestCreate(BaseModel):
    nombre: str = Field(pattern="^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", description="El nombre solo puede contener letras y espacios")
    carne: str = Field(pattern=r"^\d{9}$", description="El carné debe tener exactamente 9 dígitos numéricos")
    dpi: str = Field(pattern=r"^\d{13}$", description="El DPI debe tener exactamente 13 dígitos numéricos")
    correo: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Debe ser un correo electrónico válido")
    rol: str = Field(default="Estudiante", pattern=r"^(Estudiante|Auxiliar|Profesor|Dirección)$", description="El rol debe ser Estudiante, Auxiliar, Profesor o Dirección")
    usuario: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9]+$", description="El usuario solo puede contener letras y números")
    password: str = Field(..., min_length=4, description="La contraseña debe tener al menos 4 caracteres")
    dias_permitidos: str
    hora_inicio: str
    hora_fin: str
    fecha_expiracion: Optional[str] = None

# Esto es lo que FastAPI le va a devolver a React (incluye el ID, PIN y Estado)
class AccessRequestResponse(BaseModel):
    id: int
    nombre: str
    carne: str
    dpi: str
    correo: str
    rol: Optional[str] = "Estudiante"
    usuario: Optional[str] = None
    dias_permitidos: str
    hora_inicio: str
    hora_fin: str
    pin_acceso: Optional[str] = None
    estado: str
    fecha_solicitud: datetime
    fecha_expiracion: Optional[str] = None

    class Config:
        from_attributes = True

# --- SCHEMAS PARA ADMIN ---
class AdminCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLoginRequest(BaseModel):
    usuario: str
    password: str

from pydantic import BaseModel, Field

class AdminProfileUpdate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

class ForgotPasswordRequest(BaseModel):
    username: str

class ResetPasswordRequest(BaseModel):
    recovery_key: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class AdminResponse(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

# --- SCHEMAS PARA EL TECLADO Y EL HISTORIAL ---
class PINValidation(BaseModel):
    pin: str

class AccessHistoryResponse(BaseModel):
    id: int
    nombres: str
    accion: str
    fecha: str

    class Config:
        from_attributes = True
