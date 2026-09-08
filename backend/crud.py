from sqlalchemy.orm import Session
import models
import schemas
import random

# Buscar a un admin por su usuario
def get_admin(db: Session, username: str):
    return db.query(models.Admin).filter(models.Admin.username == username).first()

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
    db.commit() # Guarda en disco
    db.refresh(db_request)
    return db_request

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
