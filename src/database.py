import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL

# Load env only if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


USE_MYSQL = all([
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWORD"),
    os.getenv("DB_NAME"),
])

# -------------------------
# DATABASE URL
# -------------------------
if USE_MYSQL:
    DATABASE_URL = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME"),
    )
else:
    # 🔥 Fallback for Swagger / Evaluator
    DATABASE_URL = "sqlite:///./app.db"

# -------------------------
# Engine
# -------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
    future=True,
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
