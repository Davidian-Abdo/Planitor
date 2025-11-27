"""
backend/db/session.py
Production-ready SQLAlchemy session manager for Planitor (Supabase-friendly).

Behavior:
 - Read DB url from (in order): os.environ["SUPABASE_URL"], streamlit secrets ("SUPABASE_URL"), .env via python-dotenv if present.
 - Create engine lazily (so tools like alembic can import without crashing in some contexts).
 - Provide `engine` (may be None until created), `get_engine()` to ensure creation, `SessionLocal`, and helpers.
 - Use sqlalchemy.text(...) when executing raw SQL checks.
"""

from __future__ import annotations
import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text as sa_text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import sessionmaker, Session as SessionType
import streamlit as st

logger = logging.getLogger(__name__)

# ---------- Configuration & URL resolution ----------
try:
    DATABASE_URL = os.environ.get("SUPABASE_URL")
    if DATABASE_URL :
        logger.debug("Using SUPABASE_URL from environment")

except Exception:
        logger.debug("could not get SUPABASE_URL")
    

# module-level "engine" is created lazily by get_engine()
_engine: Optional[Engine] = None

def get_engine() -> Engine:
    """
    Ensure and return a SQLAlchemy Engine.
    This will create the engine on first call and raise a clear error if DB URL is missing.
    """
    global _engine
    if _engine is not None:
        return _engine

    if not DATABASE_URL:
        raise RuntimeError(
            "Database URL is not configured. "
            "Set SUPABASE_URL environment variable or Streamlit secrets (SUPABASE_URL)."
        )

    # Recommended: explicit connect timeout and minimal pool tuning for serverless hosts
    connect_args = {}
    # If pg driver supports it, set a short connect timeout to fail faster
    # (psycopg2 uses connect_timeout param in dsn)
    try:
        # SQLAlchemy will pass connect_args to DBAPI connect; this is harmless if unsupported.
        connect_args = {"connect_timeout": 10}
    except Exception:
        connect_args = {}

    try:
        _engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,        # conservative defaults for hosted environments
            max_overflow=10,
            connect_args=connect_args,
            future=True
        )
        # quick smoke test: don't execute heavy queries, just a connection check
        with _engine.connect() as conn:
            conn.execute(sa_text("SELECT 1"))
        logger.info("✅ Database engine created and connection checked")
        return _engine

    except OperationalError as e:
        logger.error("❌ OperationalError while creating engine: %s", e)
        # keep _engine as None so callers can decide what to do
        raise
    except SQLAlchemyError as e:
        logger.error("❌ SQLAlchemyError while creating engine: %s", e)
        raise

# Provide module-level alias for callers that expect `engine` at import time.
# We attempt to create it immediately (useful for production), but do not hide errors.
try:
    # Try to create engine immediately if URL is present (common on deployed hosts).
    if _engine is None:
        _engine = get_engine()
except Exception as exc:
    # Log the failure but do not crash import time with obscure stack traces.
    # Higher-level code (app init or alembic) should catch and handle.
    logger.warning("Engine not created at import: %s", exc)
    _engine = None

# ---------------- Session factory ----------------
# SessionLocal is bound if engine exists; if engine is None, callers should call get_engine() first.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, future=True, bind=_engine)  # type: ignore[arg-type]

def get_db_session() -> SessionType:
    """
    Return a new SQLAlchemy Session. Ensures engine exists first.
    Usage:  session = get_db_session()
    """
    try:
        if _engine is None:
            # attempt to create engine now (will raise a clear error if missing)
            get_engine()
            # rebind SessionLocal to the engine we just created
            global SessionLocal
            SessionLocal.configure(bind=_engine)  # type: ignore[attr-defined]
        return SessionLocal()
    except Exception as e:
        logger.error("❌ Error creating database session: %s", e)
        raise

# ---------- Transaction helpers ----------
def safe_commit(session: SessionType, context: str = "Operation") -> bool:
    try:
        session.commit()
        logger.debug("✅ Commit succeeded (%s)", context)
        return True
    except Exception as e:
        logger.error("❌ Commit failed (%s): %s", context, e)
        try:
            session.rollback()
            logger.debug("🔄 Rollback executed after failed commit (%s)", context)
        except Exception as rollback_err:
            logger.error("❌ Rollback failed (%s): %s", context, rollback_err)
        return False

def safe_rollback(session: SessionType, context: str = "Operation") -> bool:
    try:
        session.rollback()
        logger.debug("🔄 Rollback succeeded (%s)", context)
        return True
    except Exception as e:
        logger.error("❌ Rollback failed (%s): %s", context, e)
        return False

# ---------- Optional helpers ----------
def init_database() -> bool:
    """
    Optional initialization — checks the DB connectivity and optionally ensures tables exist.
    Returns True if connection is verified.
    """
    try:
        # Create a session (ensures engine exists)
        with get_db_session() as s:
            s.execute(sa_text("SELECT 1"))   # explicit sqlalchemy.text()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error("❌ Database initialization failed: %s", e)
        raise


