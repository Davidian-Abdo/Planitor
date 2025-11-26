"""
Enhanced permissions system compatible with new architecture
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Enhanced permissions for French construction roles
ROLE_PERMISSIONS = {
    'Ingénieur': [
        'project:create',
        'project:read', 
        'project:update_own',
        'schedule:generate',
        'schedule:read',
        'task:read',
        'resource:read',
        'progress:update',
        'progress:read_own'
    ],
    'Directeur': [
        'project:create',
        'project:read',
        'project:update_all', 
        'project:delete',
        'schedule:generate',
        'schedule:read',
        'schedule:optimize',
        'task:create',
        'task:update',
        'task:read',
        'resource:manage',
        'resource:read',
        'progress:update',
        'progress:read_all',
        'report:generate',
        'template:manage'
    ],
    'Admin': [
        'project:create',
        'project:read', 
        'project:update_all',
        'project:delete_all',
        'schedule:generate',
        'schedule:read',
        'schedule:optimize',
        'schedule:delete',
        'task:create',
        'task:update', 
        'task:delete',
        'task:read',
        'resource:manage',
        'resource:read',
        'progress:update',
        'progress:read_all',
        'report:generate',
        'template:manage',
        'user:manage',
        'user:read',
        'system:configure'
    ]
}

def check_permission(user_role: str, permission: str) -> bool:
    """
    Enhanced permission checking compatible with new architecture
    
    Args:
        user_role: User's role (Ingénieur, Directeur, Admin)
        permission: Permission to check
        
    Returns:
        bool: True if user has permission
    """
    try:
        if not user_role or not permission:
            return False
        
        # Normalize role
        user_role = user_role.lower()
        
        # Get permissions for role
        role_perms = ROLE_PERMISSIONS.get(user_role, [])
        
        # Check if permission is granted
        has_perm = permission in role_perms
        
        if not has_perm:
            logger.debug(f"Permission denied: {user_role} cannot {permission}")
        
        return has_perm
        
    except Exception as e:
        logger.error(f"Error checking permission: {e}")
        return False

def has_role(user_role: str, required_role: str) -> bool:
    """
    Check if user has at least the required role level
    
    Args:
        user_role: User's current role
        required_role: Minimum required role level
        
    Returns:
        bool: True if user meets role requirement
    """
    role_hierarchy = {
        'Ingénieur': 1,
        'Directeur': 2,
        'Admin': 3
    }
    
    user_level = role_hierarchy.get(user_role.lower(), 0)
    required_level = role_hierarchy.get(required_role.lower(), 0)
    
    return user_level >= required_level

def get_user_permissions(user_role: str) -> List[str]:
    """
    Get all permissions for a user role
    
    Args:
        user_role: User's role
        
    Returns:
        List of permission strings
    """
    return ROLE_PERMISSIONS.get(user_role.lower(), []).copy()
def can_access_project(user_role: str, project_user_id: int, current_user_id: int) -> bool:
    """
    Check if user can access a specific project
    
    Args:
        user_role: User's role
        project_user_id: ID of user who owns the project
        current_user_id: ID of current user
        
    Returns:
        bool: True if user can access the project
    """
    # Admins and managers can access all projects
    if has_role(user_role, 'Directeur'):
        return True
    
    # Regular users can only access their own projects
    return project_user_id == current_user_id

def can_modify_project(user_role: str, project_user_id: int, current_user_id: int) -> bool:
    """
    Check if user can modify a specific project
    
    Args:
        user_role: User's role
        project_user_id: ID of user who owns the project
        current_user_id: ID of current user
        
    Returns:
        bool: True if user can modify the project
    """
    # Admins can modify all projects
    if user_role == 'Admin':
        return True
    
    # Managers can modify all projects except admin-owned (if needed)
    if user_role == 'Directeur':
        return True
    
    # Regular users can only modify their own projects
    return project_user_id == current_user_id

def get_permission_hierarchy() -> Dict[str, Any]:
    """
    Get complete permission hierarchy for UI display
    
    Returns:
        Dict with permission hierarchy information
    """
    return {
        'roles': {
            'Ingénieur': {
                'level': 1,
                'description': 'Utilisateur standard - Gère ses propres projets',
                'permissions': ROLE_PERMISSIONS['Ingénieur']
            },
            'Directeur': {
                'level': 2, 
                'description': 'Directeur - Gère tous les projets et équipes',
                'permissions': ROLE_PERMISSIONS['Directeur']
            },
            'Admin': {
                'level': 3,
                'description': 'Administrateur - Accès complet au système',
                'permissions': ROLE_PERMISSIONS['Admin']
            }
        },
        'permission_categories': {
            'project': 'Gestion des projets',
            'schedule': 'Gestion des plannings', 
            'task': 'Gestion des tâches',
            'resource': 'Gestion des ressources',
            'progress': 'Suivi de progression',
            'report': 'Génération de rapports',
            'template': 'Gestion des templates',
            'user': 'Gestion des utilisateurs',
            'system': 'Configuration système'
        }
    }

def validate_user_action(user_role: str, action: str, resource_owner_id: int = None, 
                        current_user_id: int = None) -> Dict[str, Any]:
    """
    Validate if user can perform an action on a resource
    
    Args:
        user_role: User's role
        action: Action to perform
        resource_owner_id: ID of resource owner (optional)
        current_user_id: ID of current user (optional)
        
    Returns:
        Dict with validation results
    """
    result = {
        'allowed': False,
        'reason': '',
        'required_permission': None
    }
    
    # Map actions to permissions
    action_permission_map = {
        'create_project': 'project:create',
        'view_project': 'project:read',
        'edit_project': 'project:update_own',
        'delete_project': 'project:delete',
        'generate_schedule': 'schedule:generate',
        'view_schedule': 'schedule:read',
        'optimize_schedule': 'schedule:optimize',
        'create_task': 'task:create',
        'edit_task': 'task:update',
        'manage_resources': 'resource:manage',
        'view_resources': 'resource:read',
        'update_progress': 'progress:update',
        'view_all_progress': 'progress:read_all',
        'generate_report': 'report:generate',
        'manage_templates': 'template:manage',
        'manage_users': 'user:manage',
        'configure_system': 'system:configure'
    }
    
    required_permission = action_permission_map.get(action)
    
    if not required_permission:
        result['reason'] = f"Action non reconnue: {action}"
        return result
    
    result['required_permission'] = required_permission
    
    # Check basic permission
    if not check_permission(user_role, required_permission):
        result['reason'] = f"Permission insuffisante: {required_permission}"
        return result
    
    # Check resource ownership for specific actions
    if resource_owner_id and current_user_id:
        if 'own' in required_permission and resource_owner_id != current_user_id:
            if not has_role(user_role, 'Directeur'):
                result['reason'] = "Accès non autorisé à cette ressource"
                return result
    
    result['allowed'] = True
    return result