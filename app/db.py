from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # SQLite doesn't support connection pooling, so use default settings
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,  # Verify connections before using
    )
else:
    # For PostgreSQL, MySQL, etc. - configure connection pooling
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_size=10,          # Number of connections to maintain
        max_overflow=20,       # Additional connections allowed
        pool_pre_ping=True,    # Verify connections before using
        pool_recycle=3600,     # Recycle connections after 1 hour
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
