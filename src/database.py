from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed in CI, that's fine


# -------------------------
# Decide DB TYPE
# -------------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))


USE_MYSQL = all([DB_USER, DB_PASSWORD, DB_NAME])


# -------------------------
# Build DATABASE URL
# -------------------------
if USE_MYSQL:
    DATABASE_URL = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )
else:
    # ✅ SAFE FALLBACK (CI / Instructor / Tests)
    DATABASE_URL = "sqlite:///./test.db"


# -------------------------
# Engine
# -------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in str(DATABASE_URL) else {},
    pool_pre_ping=True,
    future=True,
)


# -------------------------
# Session Factory
# -------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# -------------------------
# Base Class
# -------------------------
class Base(DeclarativeBase):
    pass


# -------------------------
# Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
