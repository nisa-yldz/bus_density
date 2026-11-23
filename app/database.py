import sqlite3
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Proje kök dizini ve ortak veritabanı dosyası
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bus_density.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy (senin yapın)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Saf sqlite3 bağlantısı (Eda'nın routes.py kodu için aynı veritabanına yönlendirildi)
def connect_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db