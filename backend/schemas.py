from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- SCHEMAS PARA SOLICITUDES (AccessRequest) ---

# Esto es lo que React nos va a enviar cuando alguien llene el formulario
class AccessRequestCreate(BaseModel):
    nombre: str
    carne: str
    dpi: str
    correo: str
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
