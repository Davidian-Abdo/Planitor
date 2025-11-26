# backend/core/error_handler.py
"""
Unified Error Handling System
"""
import logging
from typing import Any, Optional, Dict, Union
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error with consistent structure"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: Dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class ErrorHandler:
    """Professional error handling with consistent patterns"""
    
    # Standard error codes
    ERROR_CODES = {
        'VALIDATION_ERROR': 'Data validation failed',
        'AUTH_ERROR': 'Authentication failed',
        'NOT_FOUND': 'Resource not found',
        'PERMISSION_DENIED': 'Insufficient permissions',
        'DATABASE_ERROR': 'Database operation failed',
        'INTEGRITY_ERROR': 'Data integrity violation'
    }
    
    @classmethod
    def handle_error(cls, 
                   operation: str, 
                   error: Exception,
                   return_none: bool = False,
                   log_level: str = 'ERROR') -> Optional[Any]:
        """
        Unified error handling with consistent return patterns
        
        Args:
            operation: Description of the operation
            error: Exception that occurred
            return_none: Whether to return None on error
            log_level: Logging level
            
        Returns:
            None if return_none=True, otherwise raises AppError
        """
        # Log the error
        log_method = getattr(logger, log_level.lower(), logger.error)
        log_method(f"Error in {operation}: {error}", exc_info=True)
        
        # Convert to AppError if needed
        if not isinstance(error, AppError):
            error = cls._categorize_error(error, operation)
        
        if return_none:
            return None
        else:
            raise error
    
    @classmethod
    def _categorize_error(cls, error: Exception, operation: str) -> AppError:
        """Categorize generic exceptions into AppError types"""
        if isinstance(error, SQLAlchemyError):
            return AppError(
                message=f"Database error in {operation}",
                code="DATABASE_ERROR",
                details={'original_error': str(error)}
            )
        elif isinstance(error, ValueError):
            return AppError(
                message=f"Validation error in {operation}: {error}",
                code="VALIDATION_ERROR",
                details={'original_error': str(error)}
            )
        elif isinstance(error, PermissionError):
            return AppError(
                message=f"Permission denied for {operation}",
                code="PERMISSION_DENIED",
                details={'original_error': str(error)}
            )
        else:
            return AppError(
                message=f"Unexpected error in {operation}: {error}",
                code="UNKNOWN_ERROR",
                details={'original_error': str(error)}
            )

def error_decorator(return_none: bool = False, log_level: str = 'ERROR'):
    """Decorator for consistent error handling in functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return ErrorHandler.handle_error(
                    operation=f"{func.__module__}.{func.__name__}",
                    error=e,
                    return_none=return_none,
                    log_level=log_level
                )
        return wrapper
    return decorator