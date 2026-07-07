from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# SQLite needs check_same_thread=False because FastAPI can hand a request
# off to a different thread than the one that opened the connection.
# pool_pre_ping guards against stale connections when DATABASE_URL points
# at a real network database (Postgres, etc.) instead of local SQLite.
connect_args = {}
engine_kwargs = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
