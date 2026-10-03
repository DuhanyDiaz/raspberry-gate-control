from sqlalchemy.orm import Session
import models
import schemas
import auth
import random
from datetime import datetime

# Limpiar solicitudes expiradas automáticamente
def get_admin(db: Session, username: str):
    return db.query(models.Admin).filter(models.Admin.username == username).first()

def update_admin_profile(db: Session, current_username: str, new_username: str, full_name: str, email: str):
    admin = get_admin(db, current_username)
    if admin:
        admin.username = new_username
        admin.full_name = full_name
        admin.email = email
        db.commit()
        db.refresh(admin)
    return admin

def set_recovery_key(db: Session, username: str, key_hash: str):
    admin = get_admin(db, username)
    if admin:
        admin.recovery_key = key_hash
        db.commit()
        db.refresh(admin)
    return admin

def reset_admin_password(db: Session, username: str, new_password_hashed: str):
    admin = get_admin(db, username)
    if admin:
        admin.hashed_password = new_password_hashed
        admin.recovery_key = None # Clear the key after using it
        db.commit()
        db.refresh(admin)
    return admin

def change_admin_password(db: Session, username: str, new_password_hashed: str):
    admin = get_admin(db, username)
    if admin:
        admin.hashed_password = new_password_hashed
        db.commit()
        db.refresh(admin)
    return admin

def authenticate_user(db: Session, usuario: str, password: str):
    user_request = db.query(models.AccessRequest).filter(
        models.AccessRequest.usuario == usuario
    ).first()
    
    if user_request and auth.verify_password(password, user_request.password):
        # Migración automática si la contraseña todavía estaba en texto plano
        if user_request.password and not user_request.password.startswith(("$2b$", "$2a$")):
            user_request.password = auth.get_password_hash(password)
            db.commit()
            db.refresh(user_request)
        return user_request
    return None

# Crear una solicitud nueva (cuando el alumno llena el formulario)
def create_request(db: Session, request: schemas.AccessRequestCreate):
    # Buscar si ya existe una solicitud con el mismo carné, DPI o usuario
    conflicts = db.query(models.AccessRequest).filter(
        (models.AccessRequest.carne == request.carne) |
        (models.AccessRequest.dpi == request.dpi) |
        (models.AccessRequest.usuario == request.usuario)
    ).all()
    
    # Si existen conflictos, verificamos si fueron denegadas
    for c in conflicts:
        if c.estado == "DENEGADA":
            db.delete(c) # Borramos la denegada para permitirle volver a aplicar
        else:
            return "CONFLICT" # Ya hay una activa (Aprobada o Pendiente)
    
    db.commit() # Aplicar los borrados si hubo
    
    # Hasheamos la contraseña con Bcrypt antes de guardarla en la base de datos
    hashed_pwd = auth.get_password_hash(request.password)

    db_request = models.AccessRequest(
        nombre=request.nombre,
        carne=request.carne,
        dpi=request.dpi,
        correo=request.correo,
        rol=request.rol,
        usuario=request.usuario,
        password=hashed_pwd,
        dias_permitidos=request.dias_permitidos,
        hora_inicio=request.hora_inicio,
        hora_fin=request.hora_fin,
        fecha_expiracion=request.fecha_expiracion
    )
    db.add(db_request)
    try:
        db.commit() # Guarda en disco
        db.refresh(db_request)
        return db_request
    except Exception:
        db.rollback()
        return None

def cleanup_expired_requests(db: Session):
    hoy_str = datetime.now().strftime("%Y-%m-%d")
    expiradas = db.query(models.AccessRequest).filter(
        models.AccessRequest.fecha_expiracion != None,
        models.AccessRequest.fecha_expiracion < hoy_str
    ).all()
    
    if expiradas:
        for req in expiradas:
            db.delete(req)
        db.commit()

# Obtener todas las solicitudes pendientes para llenar la tabla del Dashboard
def get_pending_requests(db: Session):
    cleanup_expired_requests(db)
    return db.query(models.AccessRequest).filter(models.AccessRequest.estado == "PENDIENTE").all()

# Obtener todas las solicitudes aprobadas
def get_approved_requests(db: Session):
    cleanup_expired_requests(db)
    return db.query(models.AccessRequest).filter(models.AccessRequest.estado == "APROBADA").all()

# Eliminar una solicitud (Finalizar acceso)
def delete_request(db: Session, request_id: int, admin_username: str = "Admin"):
    db_request = db.query(models.AccessRequest).filter(models.AccessRequest.id == request_id).first()
    if db_request:
        log_admin_action(db, admin_username, f"Finalizó/Eliminó la solicitud de {db_request.nombre} ({db_request.carne})")
        db.delete(db_request)
        db.commit()
        return True
    return False

# Registrar una acción de administrador en el historial
def log_admin_action(db: Session, admin_username: str, accion: str):
    nuevo_registro = models.AccessHistory(
        carne_usado=admin_username, # Reusamos este campo para guardar el usuario
        fue_exitoso=True,
        accion_texto=accion
    )
    db.add(nuevo_registro)
    db.commit()

# Aprobar una solicitud generamos el PIN Aleatorio
def approve_request(db: Session, request_id: int, admin_username: str = "Admin"):
    db_request = db.query(models.AccessRequest).filter(models.AccessRequest.id == request_id).first()
    if db_request:
        # Generamos un numero aleatorio de 4 digitos ejemplo "0045" o "8492"
        nuevo_pin = str(random.randint(0, 9999)).zfill(4)
        db_request.pin_acceso = nuevo_pin
        db_request.estado = "APROBADA"
        db.commit()
        db.refresh(db_request)
        log_admin_action(db, admin_username, f"Aprobó la solicitud de {db_request.nombre} ({db_request.carne})")
    return db_request

# Denegar una solicitud
def deny_request(db: Session, request_id: int, admin_username: str = "Admin"):
    db_request = db.query(models.AccessRequest).filter(models.AccessRequest.id == request_id).first()
    if db_request:
        db_request.estado = "DENEGADA"
        db.commit()
        db.refresh(db_request)
        log_admin_action(db, admin_username, f"Denegó la solicitud de {db_request.nombre} ({db_request.carne})")
    return db_request

# Validar un PIN en la cerradura
def validate_pin(db: Session, pin: str):
    # Obtenemos las solicitudes aprobadas
    solicitudes_aprobadas = db.query(models.AccessRequest).filter(
        models.AccessRequest.estado == "APROBADA"
    ).all()
    
    # Comparamos el PIN ingresado con el PIN descifrado de cada solicitud
    pin_limpio = str(pin).strip()
    for req in solicitudes_aprobadas:
        if req.pin_acceso == pin_limpio:
            return req
    return None

# Registrar intento en el historial
def log_access(db: Session, carne: str, exito: bool):
    nuevo_registro = models.AccessHistory(
        carne_usado=carne,
        fue_exitoso=exito
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro

# Obtener historial para el Admin Panel
def get_history(db: Session):
    # Obtenemos los registros ordenados por fecha descendente
    return db.query(models.AccessHistory).order_by(models.AccessHistory.fecha_hora.desc()).all()
