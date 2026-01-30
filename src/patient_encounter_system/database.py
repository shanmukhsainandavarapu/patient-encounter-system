from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL

# -------------------------
# DB CONFIG (Your config)
# -------------------------
DB_CONFIG = {
    "host": "cp-15.webhostbox.net",
    "user": "mongouhd_evernorth",
    "password": "U*dgQkKRuEHe",
    "database": "mongouhd_evernorth",
    "port": 3306,
}

# -------------------------
# Build MySQL URL
# -------------------------
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    database=DB_CONFIG["database"],
)

# -------------------------
# Engine
# -------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # avoids stale connections
    pool_recycle=3600,       # recycle connections hourly
    echo=False,              # set True for debugging SQL
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
# Dependency for FastAPI
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
