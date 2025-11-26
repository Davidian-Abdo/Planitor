"""
FIXED AuthManager with proper session injection
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session

from backend.utils.security.password_utils import hash_password, verify_password
from ..models.db_models import UserDB
from backend.services.user_service import UserService  # ✅ Fixed import

logger = logging.getLogger(__name__)

class AuthManager:
    """
    FIXED authentication manager with proper session usage
    """
    
    def __init__(self, db_session: Session, secret_key: str = "construction_planner_secret_2024"):

        self.db_session = db_session  # ✅ Use injected session
        self.secret_key = secret_key
        self.user_service = UserService(db_session)  # ✅ Pass session to service
        self.token_expiry_hours = 24
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user and return SessionManager-compatible user info
        """
        try:
            logger.info(f"Authentication attempt for user: {username}")
            
            # Get user from database using injected session
            user = self.user_service.authenticate_user(username, password)
            
            if user and user.is_active:
                # Generate JWT token
                token = self._generate_token(user)
                
                # SessionManager-compatible user info
                user_info = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'full_name': user.full_name or user.username,
                    'token': token,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
                
                # Update last login
                self.user_service.update_user_last_login(user.id)
                
                logger.info(f"User {username} authenticated successfully")
                return user_info
            
            logger.warning(f"Authentication failed for user: {username}")
            return None
            
        except Exception as e:
            logger.error(f"Error during authentication for {username}: {e}")
            return None
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: str = "", role: str = "user") -> Optional[Dict[str, Any]]:
        """
        Register a new user with SessionManager-compatible response
        
        Args:
            username: Unique username
            email: User email
            password: Plain text password
            full_name: User's full name
            role: User role (user, manager, admin)
            
        Returns:
            Dict with user info compatible with SessionManager
        """
        try:
            logger.info(f"Registration attempt for user: {username}")
            
            valid_roles = ["admin", "ingénieur", "directeur"]
            # ✅ Validate role
            if role.lower() not in valid_roles:
                logger.error(f"Invalid role provided: {role}")
                return None

            # Create new user
            user = self.user_service.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                role=role
            )
            
            if user:
                # Generate token for immediate login
                token = self._generate_token(user)
                
                # ✅ SessionManager-compatible response
                user_info = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'full_name': user.full_name or user.username,
                    'token': token,
                    'created_at': user.created_at.isoformat()
                }
                
                logger.info(f"User {username} registered successfully")
                return user_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error during registration for {username}: {e}")
            return None
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return SessionManager-compatible user info
        
        Args:
            token: JWT token to validate
            
        Returns:
            Dict with user info if valid, None otherwise
        """
        try:
            if not token:
                return None
            
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check expiration
            if datetime.fromtimestamp(payload['exp']) < datetime.now():
                logger.warning("Token has expired")
                return None
            
            # Get user from database
            user_id = payload['user_id']
            user = self.user_service.get_user_by_id(user_id)
            
            if user and user.is_active:
                # ✅ SessionManager-compatible format
                user_info = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'full_name': user.full_name or user.username
                }
                return user_info
            
            return None
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token signature has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token provided")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    def _generate_token(self, user: UserDB) -> str:
        """
        Generate JWT token for user
        
        Args:
            user: User database object
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.now() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.now()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    # Other methods remain the same but ensure SessionManager compatibility
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password with verification"""
        try:
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return False
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                logger.warning(f"Current password verification failed for user {user_id}")
                return False
            
            # Change password
            success = self.user_service.change_password(user_id, current_password, new_password)
            
            if success:
                logger.info(f"Password changed successfully for user {user_id}")
            else:
                logger.warning(f"Password change failed for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength against security requirements
        
        Args:
            password: Password to validate
            
        Returns:
            Dict with validation results
        """
        from auth_config import validate_password_strength
        return validate_password_strength(password)



    def refresh_token(self, old_token: str) -> Optional[str]:
        """
        Refresh an expired token
        
        Args:
            old_token: Expired token to refresh
            
        Returns:
            New token if successful, None otherwise
        """
        try:
            # Validate old token (even if expired)
            payload = jwt.decode(old_token, self.secret_key, algorithms=["HS256"], options={"verify_exp": False})
            
            user_id = payload['user_id']
            user = self.user_service.get_user_by_id(user_id)
            
            if user and user.is_active:
                new_token = self._generate_token(user)
                logger.info(f"Token refreshed for user {user.username}")
                return new_token
            
            return None
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
    def logout_user(self, user_id: int, token: str = None) -> bool:
        """
        Logout user and invalidate token (placeholder for future implementation)
        
        Args:
            user_id: User ID
            token: Specific token to invalidate (optional)
            
        Returns:
            bool: True if logout successful
        """
        # In a production system, you would:
        # 1. Add token to blacklist
        # 2. Remove from active sessions
        # 3. Log the logout event
        
        logger.info(f"User {user_id} logged out")
        return True


    def update_user_last_login(self, user_id: int) -> bool:
        """
        Update user's last login timestamp
        Args:
        user_id: User ID to update
        Returns:
        bool: True if updated successfully
        """
        try:
            success = self.user_service.update_user_last_login(user_id)
            if success:
                logger.info(f"Updated last login for user {user_id}")
            else:
                logger.warning(f"Failed to update last login for user {user_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")

    def deactivate_user(self, user_id: int, admin_user_id: int) -> bool:
        """
        Deactivate a user account (admin only)
        
        Args:
            user_id: User ID to deactivate
            admin_user_id: Admin user ID performing the action
            
        Returns:
            bool: True if deactivated successfully
        """
        try:
            # Verify admin privileges
            admin_user = self.user_service.get_user_by_id(admin_user_id)
            if not admin_user or admin_user.role != 'admin':
                logger.warning(f"User {admin_user_id} attempted to deactivate user without admin privileges")
                return False
            
            success = self.user_service.deactivate_user(user_id)
            
            if success:
                logger.info(f"User {user_id} deactivated by admin {admin_user_id}")
            else:
                logger.warning(f"Failed to deactivate user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False
    