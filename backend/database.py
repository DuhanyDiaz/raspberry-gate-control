from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Le decimos a SQLite que guarde todo en un archivo llamado "accesos_EMI.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./accesos_EMI.db"

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
