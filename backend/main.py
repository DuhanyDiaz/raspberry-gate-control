from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
import crud
import auth
import rate_limiter
from database import engine, get_db

# Esto obliga a SQLAlchemy a crear el archivo accesos_EMI.db y todas las tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Accesos EMI")

# SÚPER IMPORTANTE: CORS
# Esto permite que tu Frontend de React (puerto 5173) no sea bloqueado por seguridad al hablarle a Python (puerto 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"mensaje": "Servidor de Control de Accesos FIUSAC activo"}

# --- RUTAS DE ADMINISTRADOR ---
@app.post("/api/admin/login")
def login_admin(admin_data: schemas.AdminCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"admin_login:{client_ip}"

    # 1. Comprobar si la IP está bloqueada por exceder 5 intentos fallidos
    is_blocked, remaining = rate_limiter.limiter.check_is_blocked(key)
    if is_blocked:
        raise HTTPException(
            status_code=429,
            detail=f"Has superado el límite de 5 intentos fallidos. Acceso bloqueado temporalmente por {remaining} segundos."
        )

    admin = crud.get_admin(db, admin_data.username)
    if not admin or not auth.verify_password(admin_data.password, admin.hashed_password):
        now_blocked, remaining_attempts, block_seconds = rate_limiter.limiter.record_failure(key)
        if now_blocked:
            crud.log_admin_action(db, "SISTEMA", f"ALERTA: Bloqueo de login Admin por 5 intentos fallidos (IP: {client_ip})")
            raise HTTPException(
                status_code=429,
                detail=f"Has superado el límite de 5 intentos. Bloqueado temporalmente por {block_seconds} segundos."
            )
        raise HTTPException(
            status_code=401,
            detail=f"Usuario o contraseña incorrectos. Intentos restantes: {remaining_attempts}"
        )
    
    # Éxito: reiniciamos el contador de fallos
    rate_limiter.limiter.reset(key)

    # Emitimos el Token JWT firmado para autorizar las operaciones del administrador
    token = auth.create_access_token(data={"sub": admin.username, "role": "admin"})
    return {
        "mensaje": "Login exitoso",
        "username": admin.username,
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/api/admin/me", response_model=schemas.AdminResponse)
def get_admin_profile(username: str, db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    admin = crud.get_admin(db, username)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    return admin

@app.put("/api/admin/profile")
def update_profile(username: str, profile_data: schemas.AdminProfileUpdate, db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    admin = crud.update_admin_profile(db, username, profile_data.username, profile_data.full_name, profile_data.email)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    return {"mensaje": "Perfil actualizado correctamente"}

import random
import string

@app.post("/api/admin/forgot-password")
def forgot_password(req: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    admin = crud.get_admin(db, req.username)
    if not admin:
        # Por seguridad no decimos que el usuario no existe
        return {"mensaje": "Si el usuario existe, se enviará una llave a su correo"}
    
    # Generar llave de 6 caracteres
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    key_hash = auth.hash_recovery_key(key)
    crud.set_recovery_key(db, admin.username, key_hash)
    
    print(f"\n=======================================================")
    print(f"📧 [CORREO SIMULADO] Para: {admin.email or 'CORREO_NO_CONFIGURADO'}")
    print(f"Asunto: Recuperación de contraseña - Panel EMI")
    print(f"Tu llave temporal de recuperación es: {key}")
    print(f"=======================================================\n")
    
    return {"mensaje": "Si el usuario existe, se enviará una llave a su correo", "simulated_key": key}

@app.post("/api/admin/reset-password")
def reset_password(req: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    # Calculamos el hash de la llave recibida
    key_hash = auth.hash_recovery_key(req.recovery_key)
    
    # Buscar qué admin tiene el hash de esta llave (o soporte retrocompatible)
    admin = db.query(models.Admin).filter(
        (models.Admin.recovery_key == key_hash) | (models.Admin.recovery_key == req.recovery_key)
    ).first()
    if not admin:
        raise HTTPException(status_code=400, detail="Llave de recuperación inválida o expirada")
    
    # Hashear nueva contraseña
    hashed = auth.get_password_hash(req.new_password)
    crud.reset_admin_password(db, admin.username, hashed)
    
    return {"mensaje": "Contraseña actualizada exitosamente"}

@app.put("/api/admin/change-password")
def change_password(username: str, req: schemas.ChangePasswordRequest, db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    admin = crud.get_admin(db, username)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    
    if not auth.verify_password(req.current_password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="La contraseña actual es incorrecta")
        
    hashed = auth.get_password_hash(req.new_password)
    crud.change_admin_password(db, username, hashed)
    
    return {"mensaje": "Contraseña cambiada exitosamente"}

# 1. Ruta para que el Alumno envíe su formulario
@app.post("/api/solicitudes", response_model=schemas.AccessRequestResponse)
def crear_solicitud(solicitud: schemas.AccessRequestCreate, db: Session = Depends(get_db)):
    db_request = crud.create_request(db=db, request=solicitud)
    if db_request == "CONFLICT":
        raise HTTPException(status_code=400, detail="Ya tienes una solicitud activa (Pendiente o Aprobada) con ese Carné, DPI o Usuario.")
    elif not db_request:
        raise HTTPException(status_code=400, detail="Ocurrió un error al registrar la solicitud.")
    return db_request

from typing import List

# 2. Ruta para que el Panel Admin lea las solicitudes pendientes
@app.get("/api/solicitudes/pendientes", response_model=List[schemas.AccessRequestResponse])
def obtener_pendientes(db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    return crud.get_pending_requests(db=db)

# 2.5 Ruta para leer solicitudes aprobadas activas
@app.get("/api/solicitudes/aprobadas", response_model=List[schemas.AccessRequestResponse])
def obtener_aprobadas(db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    return crud.get_approved_requests(db=db)

# 2.6 Ruta para finalizar (eliminar) una solicitud aprobada
@app.delete("/api/solicitudes/{solicitud_id}/finalizar")
def finalizar_solicitud(solicitud_id: int, admin_username: str = "Admin", db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    exito = crud.delete_request(db, request_id=solicitud_id, admin_username=admin_username)
    if not exito:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return {"mensaje": "Solicitud finalizada y eliminada correctamente"}

# 3. Ruta para que el Admin APROBÉ una solicitud (Genera el PIN y enviará el correo)
@app.put("/api/solicitudes/{solicitud_id}/aprobar", response_model=schemas.AccessRequestResponse)
def aprobar_solicitud(solicitud_id: int, admin_username: str = "Admin", db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    solicitud = crud.approve_request(db, request_id=solicitud_id, admin_username=admin_username)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # TODO: Aquí programaremos el envío de correo real después
    print(f"\n[CORREO SIMULADO] -> Enviando a {solicitud.correo}...")
    print(f"Tu PIN de acceso al laboratorio EMI es: {solicitud.pin_acceso}\n")
    
    return solicitud

# 4. Ruta para Denegar
@app.put("/api/solicitudes/{solicitud_id}/denegar")
def denegar_solicitud(solicitud_id: int, admin_username: str = "Admin", db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    solicitud = crud.deny_request(db, request_id=solicitud_id, admin_username=admin_username)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return {"mensaje": "Solicitud denegada correctamente"}

@app.post("/api/usuario/login", response_model=schemas.AccessRequestResponse)
def login_usuario(datos: schemas.UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"user_login:{client_ip}:{datos.usuario}"

    is_blocked, remaining = rate_limiter.limiter.check_is_blocked(key)
    if is_blocked:
        raise HTTPException(
            status_code=429,
            detail=f"Has superado el límite de 5 intentos fallidos. Acceso bloqueado temporalmente por {remaining} segundos."
        )

    crud.cleanup_expired_requests(db) # Limpiar las expiradas al iniciar sesión
    solicitud = crud.authenticate_user(db, usuario=datos.usuario, password=datos.password)
    if not solicitud:
        now_blocked, remaining_attempts, block_seconds = rate_limiter.limiter.record_failure(key)
        if now_blocked:
            crud.log_admin_action(db, "SISTEMA", f"ALERTA: Bloqueo de login Usuario '{datos.usuario}' por 5 intentos fallidos (IP: {client_ip})")
            raise HTTPException(
                status_code=429,
                detail=f"Has superado el límite de 5 intentos. Bloqueado temporalmente por {block_seconds} segundos."
            )
        raise HTTPException(
            status_code=401,
            detail=f"Usuario o contraseña incorrectos. Intentos restantes: {remaining_attempts}"
        )

    # Éxito: reiniciamos el contador de fallos
    rate_limiter.limiter.reset(key)
    return solicitud

# 5. Ruta para Validar PIN en el teclado
@app.post("/api/accesos/validar")
def validar_pin(datos: schemas.PINValidation, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"keypad_pin:{client_ip}"

    # 1. Comprobar si el teclado está bloqueado por exceder 5 intentos fallidos
    is_blocked, remaining = rate_limiter.limiter.check_is_blocked(key)
    if is_blocked:
        raise HTTPException(
            status_code=429,
            detail=f"Teclado bloqueado por seguridad tras 5 intentos fallidos. Espere {remaining} segundos."
        )

    crud.cleanup_expired_requests(db) # Limpiar las expiradas antes de validar el PIN
    solicitud = crud.validate_pin(db, pin=datos.pin)
    
    if solicitud:
        # Éxito: reiniciamos los intentos fallidos
        rate_limiter.limiter.reset(key)
        crud.log_access(db, carne=solicitud.carne, exito=True)
        return {"mensaje": "Acceso Concedido", "nombre": solicitud.nombre}
    else:
        # Fallo: registrar intento fallido en el limitador
        now_blocked, remaining_attempts, block_seconds = rate_limiter.limiter.record_failure(key)
        if now_blocked:
            crud.log_admin_action(db, "SISTEMA", f"BLOQUEO TECLADO: 5 intentos fallidos consecutivos de PIN (IP: {client_ip})")
            crud.log_access(db, carne="BLOQUEO_FUERZA_BRUTA", exito=False)
            raise HTTPException(
                status_code=429,
                detail=f"Has superado el límite de 5 intentos fallidos. Teclado bloqueado por {block_seconds} segundos."
            )

        # Registramos fallo (no sabemos de quién es el PIN porque es incorrecto)
        crud.log_access(db, carne="PIN_INVÁLIDO", exito=False)
        raise HTTPException(
            status_code=401,
            detail=f"PIN incorrecto o inactivo. Te quedan {remaining_attempts} intento(s)."
        )

# 6. Ruta para obtener el Historial de Accesos en el Panel
@app.get("/api/accesos/historial")
def obtener_historial(db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)):
    historial_db = crud.get_history(db)
    
    # Transformamos el modelo de DB al formato que espera el Frontend
    respuesta = []
    for reg in historial_db:
        # Si fue exitoso, buscamos a quién pertenecía el carné para mostrar el nombre.
        # Por optimización (Fase 3), solo pondremos el carné si fue exitoso,
        # o podríamos hacer un JOIN. Para simplificar, buscaremos el nombre:
        usuario = "Desconocido"
        accion = "Intento Fallido (PIN Incorrecto)"
        
        if reg.accion_texto:
            # Es un registro de administrador
            usuario = f"Administrador ({reg.carne_usado})"
            accion = reg.accion_texto
        elif reg.fue_exitoso:
            sol = db.query(models.AccessRequest).filter(models.AccessRequest.carne == reg.carne_usado).first()
            usuario = sol.nombre if sol else reg.carne_usado
            accion = "Ingreso con PIN"

        respuesta.append({
            "id": reg.id,
            "nombres": usuario,
            "accion": accion,
            "fecha": reg.fecha_hora.strftime("%d/%m/%Y %H:%M:%S"),
            "es_admin": bool(reg.accion_texto)
        })
        
    return respuesta
