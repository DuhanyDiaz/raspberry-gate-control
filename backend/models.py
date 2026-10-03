from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime
import crypto_utils

# 1. Tabla de Administradores
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String) # Guardaremos la contraseña encriptada
    full_name = Column(String, nullable=True) # Nombre del administrador
    email = Column(String, nullable=True) # Correo para recuperación
    recovery_key = Column(String, nullable=True) # Llave temporal de recuperación

# 2. Tabla de Solicitudes de los Estudiantes
class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    carne = Column(String, unique=True, index=True)
    dpi = Column(String, unique=True)
    correo = Column(String)
    rol = Column(String, default="Estudiante")
    usuario = Column(String, nullable=True)
    password = Column(String, nullable=True)
    dias_permitidos = Column(String) # Ej: "Lunes,Miercoles"
    hora_inicio = Column(String) # Ej: "13:00"
    hora_fin = Column(String) # Ej: "16:00"
    _pin_acceso = Column("pin_acceso", String, nullable=True) # Almacenado cifrado en reposo con Fernet
    estado = Column(String, default="PENDIENTE") # Puede ser PENDIENTE, APROBADA, DENEGADA
    fecha_solicitud = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_expiracion = Column(String, nullable=True) # ISO Date format YYYY-MM-DD

    @property
    def pin_acceso(self):
        return crypto_utils.decrypt_pin(self._pin_acceso)

    @pin_acceso.setter
    def pin_acceso(self, value):
        if value and not crypto_utils.is_encrypted(value):
            self._pin_acceso = crypto_utils.encrypt_pin(value)
        else:
            self._pin_acceso = value

# 3. Tabla de Auditoría e Historial
class AccessHistory(Base):
    __tablename__ = "access_history"
    
    id = Column(Integer, primary_key=True, index=True)
    carne_usado = Column(String) # Guardamos quién intentó entrar o qué admin actuó
    fecha_hora = Column(DateTime, default=datetime.datetime.utcnow) # Cuándo lo intentó
    fue_exitoso = Column(Boolean) # ¿Pudo entrar o se le denegó?
    accion_texto = Column(String, nullable=True) # Texto personalizado de la acción
