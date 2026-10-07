import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Leemos DATABASE_URL desde variables de entorno (Supabase / Render / Producción)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Algunos proveedores como Render usan 'postgres://', SQLAlchemy requiere 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )
else:
    # Fallback a SQLite local si no hay variable de entorno
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_FILE = os.path.join(BASE_DIR, "accesos_EMI.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para que FastAPI abra y cierre la conexión automáticamente en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
