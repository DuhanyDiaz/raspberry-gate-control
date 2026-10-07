import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importamos modelos y configuración
import models
from database import Base

SUPABASE_URL = "postgresql://postgres:AHKmnVFoWiHv3IET@db.vkxojopodyzwfzcbbmlf.supabase.co:5432/postgres"

def migrar():
    print("🚀 Iniciando migración de SQLite a PostgreSQL en Supabase...")
    
    # 1. Conexión a SQLite local
    sqlite_path = os.path.join(os.path.dirname(__file__), "accesos_EMI.db")
    if not os.path.exists(sqlite_path):
        print(f" No se encontró la base de datos SQLite en: {sqlite_path}")
        return

    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    SqliteSession = sessionmaker(bind=sqlite_engine)

    # 2. Conexión a Supabase PostgreSQL
    pg_engine = create_engine(SUPABASE_URL, pool_pre_ping=True)
    PgSession = sessionmaker(bind=pg_engine)

    # 3. Crear tablas en PostgreSQL
    print("📦 Creando tablas en Supabase...")
    Base.metadata.create_all(bind=pg_engine)

    # 4. Migrar datos
    with SqliteSession() as db_sqlite, PgSession() as db_pg:
        # Migrar Admins
        admins_sqlite = db_sqlite.query(models.Admin).all()
        print(f"👤 Migrando {len(admins_sqlite)} administradores...")
        for admin in admins_sqlite:
            existente = db_pg.query(models.Admin).filter_by(username=admin.username).first()
            if not existente:
                db_pg.add(models.Admin(
                    username=admin.username,
                    hashed_password=admin.hashed_password,
                    full_name=admin.full_name,
                    email=admin.email,
                    recovery_key=admin.recovery_key
                ))
        db_pg.commit()

        # Migrar AccessRequests
        requests_sqlite = db_sqlite.query(models.AccessRequest).all()
        print(f" Migrando {len(requests_sqlite)} solicitudes...")
        for req in requests_sqlite:
            existente = db_pg.query(models.AccessRequest).filter_by(carne=req.carne).first()
            if not existente:
                nuevo = models.AccessRequest(
                    nombre=req.nombre,
                    carne=req.carne,
                    dpi=req.dpi,
                    correo=req.correo,
                    rol=req.rol,
                    usuario=req.usuario,
                    password=req.password,
                    dias_permitidos=req.dias_permitidos,
                    hora_inicio=req.hora_inicio,
                    hora_fin=req.hora_fin,
                    _pin_acceso=req._pin_acceso, # Preservar el PIN cifrado tal cual
                    estado=req.estado,
                    fecha_solicitud=req.fecha_solicitud,
                    fecha_expiracion=req.fecha_expiracion
                )
                db_pg.add(nuevo)
        db_pg.commit()

        # Migrar AccessHistory
        history_sqlite = db_sqlite.query(models.AccessHistory).all()
        print(f" Migrando {len(history_sqlite)} registros de historial...")
        for hist in history_sqlite:
            db_pg.add(models.AccessHistory(
                carne_usado=hist.carne_usado,
                fecha_hora=hist.fecha_hora,
                fue_exitoso=hist.fue_exitoso,
                accion_texto=hist.accion_texto
            ))
        db_pg.commit()

    print(" ¡Migración completada exitosamente! Todos los datos están en Supabase.")

if __name__ == "__main__":
    migrar()
