"""
Professional transaction decorators for service layer
"""
import logging
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

def read_only_operation(func: Callable) -> Callable:
    """
    Decorator for read-only operations - no transaction control needed
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"Read operation failed in {func.__name__}: {e}")
            raise
    return wrapper

def transactional_operation(operation_name: Optional[str] = None):
    """
    Decorator for write operations - validates transaction state
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            op_name = operation_name or func.__name__
            
            # Check if service has db_session
            if not hasattr(self, 'db_session'):
                raise ValueError(f"Service {self.__class__.__name__} must have db_session attribute")
            
            try:
                result = func(self, *args, **kwargs)
                logger.debug(f"✅ Transactional operation '{op_name}' completed")
                return result
                
            except Exception as e:
                logger.error(f"❌ Transactional operation '{op_name}' failed: {e}")
                raise
                
        return wrapper
    return decorator

def requires_active_transaction(func: Callable) -> Callable:
    """
    Decorator for operations that require active transaction
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        # Check if we're in a transaction context
        from backend.db.session_manager import session_manager
        if not session_manager.is_transaction_active():
            logger.warning("⚠️ Operation called outside transaction context")
        
        return func(self, *args, **kwargs)
    return wrapper