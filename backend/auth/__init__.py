"""
Authentication and authorization system for French Construction Project Planner
Integrated with SessionManager pattern
"""

from .auth_manager import AuthManager
from .session_manager import SessionManager
from .permissions import check_permission, has_role, get_user_permissions

__all__ = [
    'AuthManager',
    'SessionManager', 
    'check_permission',
    'has_role',
    'get_user_permissions'
]