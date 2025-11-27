"""
backend/db/session.py
Professional SQLAlchemy session management for Planitor
Supports Streamlit Cloud with Supabase (via st.secrets)
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SessionType
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
import streamlit as st

logger = logging.getLogger(__name__)

# --------------------------
# Database URL from Supabase secrets.toml 
try:
    DATABASE_URL  = "postgresql://postgres:ABDOABDOABDO@db.vigyqbzjtpqjzlpuyzvf.supabase.co:5432/postgres"
# --------------------------
    # st.secrets["SUPABASE_URL"]  # Hard-coded call to secrets.toml
except KeyError:
    logger.error("❌ SUPABASE_URL not found in secrets.toml. Check Streamlit Cloud configuration.")
    DATABASE_URL = None

# --------------------------
# SQLAlchemy Engine Creation
# --------------------------
def create_engine_production() -> Engine:
    if DATABASE_URL is None:
        raise RuntimeError("Database URL is not configured.")
    
    # Configure engine with connection pooling
    return create_engine(
        DATABASE_URL,
        echo=False,  # Set True for SQL logging during debugging
        pool_pre_ping=True,
        pool_size=15,
        max_overflow=20
    )

# --------------------------
# Session Factory
# --------------------------
engine = create_engine_production()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --------------------------
# Get a new database session
# --------------------------
def get_db_session() -> SessionType:
    """Return a new SQLAlchemy Session"""
    try:
        session = SessionLocal()
        return session
    except SQLAlchemyError as e:
        logger.error(f"❌ Error creating database session: {e}")
        raise

# --------------------------
# Transaction helpers
# --------------------------
def safe_commit(session: SessionType, context: str = "Unknown"):
    """Commit transaction safely"""
    try:
        session.commit()
        logger.debug(f"✅ Transaction committed: {context}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"❌ Commit failed ({context}): {e}")
        raise

def safe_rollback(session: SessionType, context: str = "Unknown"):
    """Rollback transaction safely"""
    try:
        session.rollback()
        logger.debug(f"🔄 Transaction rolled back: {context}")
    except SQLAlchemyError as e:
        logger.error(f"❌ Rollback failed ({context}): {e}")
        raise

# --------------------------
# Database initialization (optional)
# --------------------------
def init_database():
    """Test database connection"""
    try:
        with get_db_session() as session:
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

