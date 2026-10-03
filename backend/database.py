import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ruta absoluta al archivo accesos_EMI.db en el directorio del backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "accesos_EMI.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

# Configuramos el motor. 
# check_same_thread=False es necesario en SQLite cuando usamos FastAPI
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
