import logging
import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./et_agent.db")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args=connect_args,
        pool_recycle=300,
        pool_timeout=30,
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Database connection established successfully")
except OperationalError as e:
    logger.error("Failed to connect to database: %s", str(e))
    logger.warning("App will start but DB features will be unavailable")
    engine = None
except Exception as e:
    logger.error("Unexpected database error on startup: %s", str(e))
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session with proper error handling."""
    if SessionLocal is None:
        raise RuntimeError("Database is not available. Check your DATABASE_URL configuration.")

    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        logger.error("Database operational error: %s", str(e))
        db.rollback()
        raise
    except SQLAlchemyError as e:
        logger.error("Database error: %s", str(e))
        db.rollback()
        raise
    except Exception as e:
        logger.error("Unexpected error during database session: %s", str(e))
        db.rollback()
        raise
    finally:
        db.close()
