from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
import crud
import auth
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

# 1. Ruta para que el Alumno envíe su formulario
@app.post("/api/solicitudes", response_model=schemas.AccessRequestResponse)
def crear_solicitud(solicitud: schemas.AccessRequestCreate, db: Session = Depends(get_db)):
    return crud.create_request(db=db, request=solicitud)

# 2. Ruta para que el Panel Admin lea las solicitudes pendientes
@app.get("/api/solicitudes/pendientes")
def obtener_pendientes(db: Session = Depends(get_db)):
    return crud.get_pending_requests(db=db)

# 3. Ruta para que el Admin APROBÉ una solicitud (Genera el PIN y enviará el correo)
@app.put("/api/solicitudes/{solicitud_id}/aprobar")
def aprobar_solicitud(solicitud_id: int, db: Session = Depends(get_db)):
    solicitud = crud.approve_request(db, request_id=solicitud_id)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # TODO: Aquí programaremos el envío de correo real después
    print(f"\n[CORREO SIMULADO] -> Enviando a {solicitud.correo}...")
    print(f"Tu PIN de acceso al laboratorio EMI es: {solicitud.pin_acceso}\n")
    
    return solicitud

# 4. Ruta para Denegar
@app.put("/api/solicitudes/{solicitud_id}/denegar")
def denegar_solicitud(solicitud_id: int, db: Session = Depends(get_db)):
    solicitud = crud.deny_request(db, request_id=solicitud_id)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return {"mensaje": "Solicitud denegada correctamente"}

# 5. Ruta para Validar PIN en el teclado
@app.post("/api/accesos/validar")
def validar_pin(datos: schemas.PINValidation, db: Session = Depends(get_db)):
    solicitud = crud.validate_pin(db, pin=datos.pin)
    
    if solicitud:
        # Registramos éxito
        crud.log_access(db, carne=solicitud.carne, exito=True)
        return {"mensaje": "Acceso Concedido", "nombre": solicitud.nombre}
    else:
        # Registramos fallo (no sabemos de quién es el PIN porque es incorrecto)
        crud.log_access(db, carne="PIN_INVÁLIDO", exito=False)
        raise HTTPException(status_code=401, detail="PIN incorrecto o inactivo")

# 6. Ruta para obtener el Historial de Accesos en el Panel
@app.get("/api/accesos/historial")
def obtener_historial(db: Session = Depends(get_db)):
    historial_db = crud.get_history(db)
    
    # Transformamos el modelo de DB al formato que espera el Frontend
    respuesta = []
    for reg in historial_db:
        # Si fue exitoso, buscamos a quién pertenecía el carné para mostrar el nombre.
        # Por optimización (Fase 3), solo pondremos el carné si fue exitoso,
        # o podríamos hacer un JOIN. Para simplificar, buscaremos el nombre:
        usuario = "Desconocido"
        accion = "Intento Fallido (PIN Incorrecto)"
        
        if reg.fue_exitoso:
            sol = db.query(models.AccessRequest).filter(models.AccessRequest.carne == reg.carne_usado).first()
            usuario = sol.nombre if sol else reg.carne_usado
            accion = "Ingreso con PIN"

        respuesta.append({
            "id": reg.id,
            "nombres": usuario,
            "accion": accion,
            "fecha": reg.fecha_hora.strftime("%d/%m/%Y %H:%M:%S")
        })
        
    return respuesta
