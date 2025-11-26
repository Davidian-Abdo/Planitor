"""
Enhanced User service - Fully compatible with new architecture
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.db.repositories.user_repo import UserRepository
from backend.models.db_models import UserDB
from backend.utils.security.password_utils import hash_password, verify_password

logger = logging.getLogger(__name__)

class UserService:
    """
    Enhanced User service with proper dependency injection
    """
    
    def __init__(self, db_session: Session):
        # ✅ Accept and use injected db_session
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)
        self.logger = logging.getLogger(__name__)
    
    def get_user_by_id(self, user_id: int) -> Optional[UserDB]:
        """Get user by ID"""
        try:
            return self.user_repo.get_user_by_id(user_id)
        except Exception as e:
            self.logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[UserDB]:
        """Get user by username"""
        try:
            return self.user_repo.get_user_by_username(username)
        except Exception as e:
            self.logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email"""
        try:
            return self.user_repo.get_user_by_email(email)
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_all_users(self) -> List[UserDB]:
        """Get all users (admin only)"""
        try:
            return self.user_repo.get_all_users()
        except Exception as e:
            self.logger.error(f"Error getting all users: {e}")
            return []
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics for dashboard"""
        try:
            # This would typically aggregate user activity data
            return {
                'total_projects': 0,
                'active_projects': 0,
                'completed_projects': 0,
                'recent_activity': []
            }
        except Exception as e:
            self.logger.error(f"Error getting user statistics for {user_id}: {e}")
            return {}
    
    def update_user_profile(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user profile information"""
        try:
            user = self.user_repo.get_user_by_id(user_id)
            if not user:
                return False
            
            # Update allowed fields
            allowed_fields = ['full_name', 'email', 'company', 'phone']
            update_data = {k: v for k, v in updates.items() if k in allowed_fields and v is not None}
            
            if update_data:
                return self.user_repo.update_user(user_id, update_data)
            return True  # No changes needed
            
        except Exception as e:
            self.logger.error(f"Error updating user profile {user_id}: {e}")
            return False
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password with verification"""
        try:
            user = self.user_repo.get_user_by_id(user_id)
            if not user:
                return False
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                return False
            
            # Hash new password
            new_password_hash = hash_password(new_password)
            
            # Update password
            return self.user_repo.update_user(user_id, {'password_hash': new_password_hash})
            
        except Exception as e:
            self.logger.error(f"Error changing password for user {user_id}: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user"""
        try:
            return self.user_repo.update_user(user_id, {'is_active': False})
        except Exception as e:
            self.logger.error(f"Error deactivating user {user_id}: {e}")
            return False
    
    def create_user(self, username: str, email: str, password: str,
                   full_name: str = "", role: str = "user") -> Optional[UserDB]:
        """Create new user"""
        try:
            # Check for existing username
            if self.user_repo.get_user_by_username(username):
                self.logger.warning(f"Username already exists: {username}")
                return None
        
            # Check for existing email
            if self.user_repo.get_user_by_email(email):
                self.logger.warning(f"Email already exists: {email}")
                return None

            # Hash password
            password_hash = hash_password(password)

            # Prepare user data
            user_data = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name,
                "role": role,
                "is_active": True
            }

            # Create user
            user = self.user_repo.create_user(user_data)
        
            if user:
                self.logger.info(f"User created successfully: {username}")
                return user
            else:
                self.logger.error(f"User creation failed for: {username}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating user {username}: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserDB]:
        """Authenticate user with username and password"""
        try:
            # Get user by username
            user = self.user_repo.get_user_by_username(username)
        
            if not user or not user.is_active:
                self.logger.warning(f"Authentication failed - user not found or inactive: {username}")
                return None
        
            # Verify password
            if verify_password(password, user.password_hash):
                # Update last login timestamp
                self.user_repo.update_user_last_login(user.id)
                self.logger.info(f"User authenticated successfully: {username}")
                return user
            else:
                self.logger.warning(f"Authentication failed - invalid password for user: {username}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error authenticating user {username}: {e}")
            return None
    
    def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            return self.user_repo.update_user_last_login(user_id)
        except Exception as e:
            self.logger.error(f"Error updating last login for user {user_id}: {e}")
            return False
    
    # Task template methods (compatible with repository pattern)
    def get_user_task_templates(self, user_id: int, discipline: str = None) -> List[Dict[str, Any]]:
        """Get user task templates"""
        try:
            templates = self.user_repo.get_user_task_templates(user_id, discipline)
            return [self._template_to_dict(template) for template in templates]
        except Exception as e:
            self.logger.error(f"Error getting user task templates: {e}")
            return []
    
    def create_user_task_template(self, user_id: int, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new user task template"""
        try:
            template_data['user_id'] = user_id
            template = self.user_repo.create_user_task_template(template_data)
            return self._template_to_dict(template) if template else None
        except Exception as e:
            self.logger.error(f"Error creating user task template: {e}")
            return None
    
    def _template_to_dict(self, template) -> Dict[str, Any]:
        """Convert template object to dictionary"""
        return {
            'id': getattr(template, 'id', None),
            'name': getattr(template, 'name', ''),
            'discipline': getattr(template, 'discipline', ''),
            'base_duration': getattr(template, 'base_duration', 0),
            'resource_type': getattr(template, 'resource_type', ''),
            'is_active': getattr(template, 'is_active', True)
        }