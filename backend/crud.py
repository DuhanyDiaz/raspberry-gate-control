from sqlalchemy.orm import Session
import models
import schemas
import random

# Buscar a un admin por su usuario
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

def set_recovery_key(db: Session, username: str, key: str):
    admin = get_admin(db, username)
    if admin:
        admin.recovery_key = key
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

# Crear una solicitud nueva (cuando el alumno llena el formulario)
def create_request(db: Session, request: schemas.AccessRequestCreate):
    db_request = models.AccessRequest(
        nombre=request.nombre,
        carne=request.carne,
        dpi=request.dpi,
        correo=request.correo,
        dias_permitidos=request.dias_permitidos,
        hora_inicio=request.hora_inicio,
        hora_fin=request.hora_fin
    )
    db.add(db_request)
    try:
        db.commit() # Guarda en disco
        db.refresh(db_request)
        return db_request
    except Exception:
        db.rollback()
        return None

# Obtener todas las solicitudes pendientes para llenar la tabla del Dashboard
def get_pending_requests(db: Session):
    return db.query(models.AccessRequest).filter(models.AccessRequest.estado == "PENDIENTE").all()

# Aprobar una solicitud generamos el PIN Aleatorio
def approve_request(db: Session, request_id: int):
    db_request = db.query(models.AccessRequest).filter(models.AccessRequest.id == request_id).first()
    if db_request:
        # Generamos un numero aleatorio de 4 digitos ejemplo "0045" o "8492"
        nuevo_pin = str(random.randint(0, 9999)).zfill(4)
        db_request.pin_acceso = nuevo_pin
        db_request.estado = "APROBADA"
        db.commit()
        db.refresh(db_request)
    return db_request

# Denegar una solicitud
def deny_request(db: Session, request_id: int):
    db_request = db.query(models.AccessRequest).filter(models.AccessRequest.id == request_id).first()
    if db_request:
        db_request.estado = "DENEGADA"
        db.commit()
        db.refresh(db_request)
    return db_request

# Validar un PIN en la cerradura
def validate_pin(db: Session, pin: str):
    # Buscamos una solicitud aprobada que tenga este PIN
    return db.query(models.AccessRequest).filter(
        models.AccessRequest.pin_acceso == pin,
        models.AccessRequest.estado == "APROBADA"
    ).first()

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
