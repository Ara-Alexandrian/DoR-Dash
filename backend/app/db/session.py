from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create async engine for FastAPI app
async_engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True, future=True)

# Create sync engine for direct database access
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI_SYNC)

# Create session factories
async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Real database session (no longer mock)
def get_db():
    """Dependency for getting async db session"""
    return async_session()

# Synchronous session for auth
def get_sync_db() -> Session:
    """Dependency for getting synchronous db session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()