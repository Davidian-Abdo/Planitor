"""
Professional logging configuration for construction planning application
Structured logging with different levels and output handlers
"""
import logging
import logging.config
import os
from pathlib import Path
import json
from datetime import datetime

class ProfessionalLogging:
    """Professional logging configuration for construction app"""
    
    @staticmethod
    def setup_logging(log_level: str = "INFO", log_file: str = "logs/construction_planner.log"):
        """
        Setup comprehensive logging configuration
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Path to log file
        """
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'json': {
                    'format': '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s", "file": "%(filename)s", "line": "%(lineno)d"}',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'detailed',
                    'filename': log_file,
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'encoding': 'utf-8'
                },
                'error_file': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'detailed',
                    'filename': str(log_path.parent / 'errors.log'),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'encoding': 'utf-8'
                }
            },
            'loggers': {
                '': {  # Root logger
                    'handlers': ['console', 'file', 'error_file'],
                    'level': 'DEBUG',
                    'propagate': False
                },
                'backend': {
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                },
                'frontend': {
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                },
                'database': {
                    'handlers': ['console', 'file'],
                    'level': 'INFO',
                    'propagate': False
                },
                'scheduling': {
                    'handlers': ['console', 'file'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }
        
        logging.config.dictConfig(logging_config)
        
        # Log startup information
        logger = logging.getLogger(__name__)
        logger.info("🚀 Construction Project Planner logging initialized")
        logger.info(f"📝 Log level: {log_level}")
        logger.info(f"📁 Log file: {log_file}")

class PerformanceLogger:
    """Performance monitoring and logging"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.logger = logging.getLogger('performance')
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"🕒 Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"✅ Operation completed: {self.operation_name} - Duration: {duration:.2f}s")
        else:
            self.logger.error(f"❌ Operation failed: {self.operation_name} - Duration: {duration:.2f}s - Error: {exc_val}")
    
    @staticmethod
    def log_database_query(query: str, duration: float, rows_affected: int = None):
        """Log database query performance"""
        logger = logging.getLogger('database.performance')
        log_data = {
            'query_type': query.split()[0].upper() if query else 'UNKNOWN',
            'duration_seconds': duration,
            'rows_affected': rows_affected
        }
        
        if duration > 1.0:  # Log slow queries as warnings
            logger.warning(f"Slow query detected: {json.dumps(log_data)}")
        else:
            logger.debug(f"Query executed: {json.dumps(log_data)}")

class AuditLogger:
    """Audit logging for security and compliance"""
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_user_action(self, user_id: int, action: str, resource_type: str, 
                       resource_id: int = None, details: dict = None):
        """Log user actions for audit trail"""
        audit_data = {
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.logger.info(f"👤 User action: {json.dumps(audit_data)}")
    
    def log_security_event(self, event_type: str, user_id: int = None, 
                          severity: str = 'INFO', details: dict = None):
        """Log security-related events"""
        security_data = {
            'event_type': event_type,
            'user_id': user_id,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        if severity == 'ERROR':
            self.logger.error(f"🔒 Security event: {json.dumps(security_data)}")
        elif severity == 'WARNING':
            self.logger.warning(f"🔒 Security event: {json.dumps(security_data)}")
        else:
            self.logger.info(f"🔒 Security event: {json.dumps(security_data)}")
