"""
PROFESSIONAL Session Manager for Streamlit Architecture
Unified session lifecycle management with transaction control
"""
import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy.orm import Session

from backend.db.session import get_db_session, safe_commit, safe_rollback

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Professional session manager for Streamlit request lifecycle
    """
    
    def __init__(self):
        self._current_session: Optional[Session] = None
        self._transaction_active = False
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Professional session context manager for request lifecycle
        Usage:
            with session_manager.session_scope() as session:
                # Do database operations
                # Auto-commit on success, auto-rollback on exception
        """
        session = self._get_or_create_session()
        self._transaction_active = True
        
        try:
            logger.debug("🎯 Starting database transaction scope")
            yield session
            # Commit on successful completion
            safe_commit(session, "Request transaction")
            self._transaction_active = False
            logger.debug("✅ Transaction completed successfully")
            
        except Exception as e:
            # Rollback on any exception
            safe_rollback(session, f"Request transaction failed: {str(e)}")
            self._transaction_active = False
            logger.error(f"❌ Transaction rolled back due to error: {e}")
            raise
            
        finally:
            # Always close session at the end of scope
            self._close_session()
    
    def get_current_session(self) -> Optional[Session]:
        """Get current session if exists"""
        return self._current_session
    
    def _get_or_create_session(self) -> Session:
        """Get existing session or create new one"""
        if self._current_session is None:
            self._current_session = get_db_session()
            logger.debug("🆕 Created new database session")
        else:
            logger.debug("🔁 Reusing existing database session")
        return self._current_session
    
    def _close_session(self):
        """Close current session"""
        if self._current_session:
            try:
                self._current_session.close()
                logger.debug("🔒 Database session closed")
            except Exception as e:
                logger.error(f"❌ Error closing session: {e}")
            finally:
                self._current_session = None
                self._transaction_active = False
    
    def is_transaction_active(self) -> bool:
        """Check if transaction is currently active"""
        return self._transaction_active
    
    def manual_commit(self, operation_name: str = "Manual operation") -> bool:
        """Manual commit for special cases"""
        if self._current_session and self._transaction_active:
            return safe_commit(self._current_session, operation_name)
        return False
    
    def manual_rollback(self, operation_name: str = "Manual operation") -> bool:
        """Manual rollback for special cases"""
        if self._current_session and self._transaction_active:
            return safe_rollback(self._current_session, operation_name)
        return False

# Global session manager instance
session_manager = SessionManager()