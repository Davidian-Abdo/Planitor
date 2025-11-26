"""
Enhanced authentication configuration and security settings
Integrated with SessionManager pattern
"""
import streamlit as st
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SecurityConfig:
    """
    Enhanced security configuration integrated with SessionManager
    """
    
    # Session security
    SESSION_TIMEOUT_MINUTES = 120
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # Password policy
    PASSWORD_POLICY = {
        'min_length': 8,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_special_chars': True,
        'max_age_days': 90  # Password expiration
    }
    
    # JWT Token settings
    JWT_CONFIG = {
        'algorithm': 'HS256',
        'expiration_hours': 24,
        'refresh_threshold_minutes': 30
    }
    
    # Role-based access control
    ROLE_PERMISSIONS = {
        'Ingénieur': [
            'project:read', 'project:create', 'project:update_own',
            'schedule:generate', 'schedule:read',
            'task:read', 'resource:read',
            'progress:update', 'progress:read_own'
        ],
        'Directeur': [
            'project:read', 'project:create', 'project:update_all', 'project:delete',
            'schedule:generate', 'schedule:read', 'schedule:optimize',
            'task:create', 'task:update', 'task:read',
            'resource:manage', 'resource:read',
            'progress:update', 'progress:read_all',
            'report:generate', 'template:manage'
        ],
        'Admin': [
            'project:read', 'project:create', 'project:update_all', 'project:delete_all',
            'schedule:generate', 'schedule:read', 'schedule:optimize', 'schedule:delete',
            'task:create', 'task:update', 'task:delete', 'task:read',
            'resource:manage', 'resource:read',
            'progress:update', 'progress:read_all',
            'report:generate', 'template:manage',
            'user:manage', 'user:read', 'system:configure'
        ]
    }

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Comprehensive password strength validation
    
    Args:
        password: Password to validate
        
    Returns:
        Dict with validation results and suggestions
    """
    validation_result = {
        'is_valid': True,
        'score': 0,
        'issues': [],
        'suggestions': [],
        'strength': 'weak'
    }
    
    policy = SecurityConfig.PASSWORD_POLICY
    
    # Length check
    if len(password) < policy['min_length']:
        validation_result['is_valid'] = False
        validation_result['issues'].append(
            f"Password must be at least {policy['min_length']} characters"
        )
    
    # Uppercase check
    if policy['require_uppercase'] and not any(char.isupper() for char in password):
        validation_result['is_valid'] = False
        validation_result['issues'].append("Password must contain at least one uppercase letter")
    
    # Lowercase check  
    if policy['require_lowercase'] and not any(char.islower() for char in password):
        validation_result['is_valid'] = False
        validation_result['issues'].append("Password must contain at least one lowercase letter")
    
    # Numbers check
    if policy['require_numbers'] and not any(char.isdigit() for char in password):
        validation_result['is_valid'] = False
        validation_result['issues'].append("Password must contain at least one number")
    
    # Special characters check
    if policy['require_special_chars'] and not any(not char.isalnum() for char in password):
        validation_result['is_valid'] = False
        validation_result['issues'].append("Password must contain at least one special character")
    
    # Calculate strength score
    score = 0
    if len(password) >= 12: score += 2
    elif len(password) >= 6: score += 1
    
    if any(char.isupper() for char in password): score += 1
    if any(char.islower() for char in password): score += 1  
    if any(char.isdigit() for char in password): score += 1
    if any(not char.isalnum() for char in password): score += 1
    
    validation_result['score'] = score
    
    # Determine strength level
    if score >= 5:
        validation_result['strength'] = 'strong'
    elif score >= 3:
        validation_result['strength'] = 'medium'
    else:
        validation_result['strength'] = 'weak'
    
    # Provide suggestions
    if score < 3:
        validation_result['suggestions'].append("Use a combination of letters, numbers, and special characters")
    if len(password) < 6:
        validation_result['suggestions'].append("Use at least 12 characters for better security")
    
    return validation_result

def check_permission(user_role: str, permission: str) -> bool:
    """
    Check if user role has specific permission
    
    Args:
        user_role: User's role
        permission: Permission to check
        
    Returns:
        bool: True if user has permission
    """
    if not user_role:
        return False
    
    role_permissions = SecurityConfig.ROLE_PERMISSIONS.get(user_role, [])
    return permission in role_permissions

def get_user_permissions(user_role: str) -> List[str]:
    """
    Get all permissions for a user role
    
    Args:
        user_role: User's role
        
    Returns:
        List of permission strings
    """
    return SecurityConfig.ROLE_PERMISSIONS.get(user_role, []).copy()

def get_security_settings() -> Dict[str, Any]:
    """
    Get comprehensive security settings for UI display
    
    Returns:
        Dict with security configuration
    """
    return {
        'session_timeout': SecurityConfig.SESSION_TIMEOUT_MINUTES,
        'password_policy': SecurityConfig.PASSWORD_POLICY,
        'max_login_attempts': SecurityConfig.MAX_LOGIN_ATTEMPTS,
        'lockout_duration': SecurityConfig.LOCKOUT_DURATION_MINUTES,
        'jwt_config': SecurityConfig.JWT_CONFIG
    }