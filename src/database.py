import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL


# =========================
# DATABASE URL RESOLUTION
# =========================

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))


# 👉 If MySQL env vars exist → use MySQL
# 👉 Else → fallback to SQLite (evaluator / CI safe)
if DB_USER and DB_PASSWORD and DB_NAME:
    DATABASE_URL = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )
else:
    DATABASE_URL = URL.create(
        drivername="sqlite",
        database="app.db",
    )


# =========================
# ENGINE CONFIG
# =========================

# SQLite needs special args
connect_args = {}
if DATABASE_URL.drivername.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
    echo=False,
)


# =========================
# SESSION FACTORY
# =========================
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# =========================
# BASE CLASS
# =========================
class Base(DeclarativeBase):
    pass


# =========================
# FASTAPI DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
