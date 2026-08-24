import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text
from app.config.settings import settings

logger = logging.getLogger("lenny_growth.db")

Base = declarative_base()

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        # Check if DATABASE_URL PostgreSQL is explicitly configured and working
        db_url = settings.DATABASE_URL
        if "postgresql" in db_url:
            try:
                # Use SQLite fallback by default for local testing if postgres credentials fail
                _engine = create_async_engine(db_url, echo=False, future=True, pool_pre_ping=True)
            except Exception as e:
                logger.warning(f"Postgres engine creation failed: {e}. Defaulting to SQLite.")
                _engine = create_async_engine("sqlite+aiosqlite:///./lenny_growth.db", echo=False)
        else:
            _engine = create_async_engine(db_url, echo=False)
    return _engine

def AsyncSessionLocal():
    engine = get_engine()
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return async_session()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables and handle Postgres / SQLite fallback gracefully."""
    global _engine
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            if "postgresql" in str(engine.url):
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                except Exception as ext_err:
                    logger.warning(f"pgvector extension create warning: {ext_err}")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Primary database connection failed ({e}). Switching engine to local SQLite database.")
        sqlite_url = "sqlite+aiosqlite:///./lenny_growth.db"
        _engine = create_async_engine(sqlite_url, echo=False)
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite database initialized successfully.")
