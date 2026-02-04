import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL

# Optional: only needed locally
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


# -------------------------
# Decide DB type
# -------------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

USE_SQLITE = not all([DB_USER, DB_PASSWORD, DB_NAME])

# -------------------------
# Build DB URL
# -------------------------
if USE_SQLITE:
    DATABASE_URL = "sqlite:///./app.db"
else:
    DATABASE_URL = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=DB_NAME,
    )

# -------------------------
# Engine
# -------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if USE_SQLITE else {},
    pool_pre_ping=True,
    echo=False,
)

# -------------------------
# Session
# -------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# -------------------------
# Base
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
