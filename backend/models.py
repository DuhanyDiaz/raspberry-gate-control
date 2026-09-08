from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime

# 1. Tabla de Administradores
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String) # Guardaremos la contraseña encriptada

# 2. Tabla de Solicitudes de los Estudiantes
class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    carne = Column(String, unique=True, index=True)
    dpi = Column(String, unique=True)
    correo = Column(String)
    dias_permitidos = Column(String) # Ej: "Lunes,Miercoles"
    hora_inicio = Column(String) # Ej: "13:00"
    hora_fin = Column(String) # Ej: "16:00"
    pin_acceso = Column(String, nullable=True) # Estará vacío hasta que lo aprobemos
    estado = Column(String, default="PENDIENTE") # Puede ser PENDIENTE, APROBADA, DENEGADA
    fecha_solicitud = Column(DateTime, default=datetime.datetime.utcnow)

# 3. Tabla de Auditoría e Historial
class AccessHistory(Base):
    __tablename__ = "access_history"
    
    id = Column(Integer, primary_key=True, index=True)
    carne_usado = Column(String) # Guardamos quién intentó entrar
    fecha_hora = Column(DateTime, default=datetime.datetime.utcnow) # Cuándo lo intentó
    fue_exitoso = Column(Boolean) # ¿Pudo entrar o se le denegó?
