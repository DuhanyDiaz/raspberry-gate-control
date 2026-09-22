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
    dias_permitidos: str
    hora_inicio: str
    hora_fin: str

# Esto es lo que FastAPI le va a devolver a React (incluye el ID, PIN y Estado)
class AccessRequestResponse(BaseModel):
    id: int
    nombre: str
    carne: str
    dpi: str
    correo: str
    dias_permitidos: str
    hora_inicio: str
    hora_fin: str
    pin_acceso: Optional[str] = None
    estado: str
    fecha_solicitud: datetime

    class Config:
        from_attributes = True

# --- SCHEMAS PARA ADMIN ---
class AdminCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

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
