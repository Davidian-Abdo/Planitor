"""
FIXED SessionManager - Authentication state ONLY (no database transactions)
"""
import streamlit as st
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta 

logger = logging.getLogger(__name__)

class SessionManager:
    """
    FIXED: Manages USER AUTHENTICATION state only
    No database transaction control here
    """
    
    def __init__(self, session_timeout_minutes: int = 120):
        self.session_timeout_minutes = session_timeout_minutes
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize authentication session state only"""
        # Authentication state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'role' not in st.session_state:
            st.session_state.role = None
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = None
        if 'token' not in st.session_state:
            st.session_state.token = None
        
        # Backward compatibility
        if 'user' not in st.session_state:
            st.session_state.user = None
    
    def create_session(self, user_info: Dict[str, Any]) -> bool:
        """
        Create user session - AUTHENTICATION ONLY
        """
        try:
            # Authentication state
            st.session_state.user_id = user_info.get('user_id')
            st.session_state.username = user_info.get('username')
            st.session_state.role = user_info.get('role')
            st.session_state.authenticated = True
            st.session_state.login_time = datetime.now()
            st.session_state.last_activity = datetime.now()
            st.session_state.token = user_info.get('token')
            
            # Backward compatibility
            st.session_state.user = {
                'id': user_info.get('user_id'),
                'username': user_info.get('username'),
                'role': user_info.get('role'),
                'full_name': user_info.get('full_name', user_info.get('username')),
                'email': user_info.get('email', '')
            }
            
            logger.info(f"Authentication session created for user: {user_info.get('username')}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating authentication session: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check authentication state only"""
        if not st.session_state.get('authenticated', False):
            return False
        
        # Check session timeout
        if self._is_session_expired():
            logger.info(f"Authentication session expired for user: {st.session_state.username}")
            self.logout()
            return False
        
        # Update last activity
        st.session_state.last_activity = datetime.now()
        return True
    
    def _is_session_expired(self) -> bool:
        """Check if authentication session expired"""
        last_activity = st.session_state.get('last_activity')
        if not last_activity:
            return True
        
        timeout_delta = timedelta(minutes=self.session_timeout_minutes)
        return datetime.now() - last_activity > timeout_delta
    
    def logout(self):
        """
        Enhanced logout with comprehensive session cleanup
        """
        user_id = self.get_user_id()
        username = self.get_username()
        
        # Use centralized session cleaner
        from backend.utils.session_cleaner import SessionCleaner
        cleaned_count = SessionCleaner.clean_user_session(user_id)
        
        logger.info(f"User {username} (ID: {user_id}) logged out - {cleaned_count} session items cleaned")
    
    def get_user_id(self) -> Optional[int]:
        """Get current user ID"""
        return st.session_state.get('user_id')
    
    def get_username(self) -> Optional[str]:
        """Get current username"""
        return st.session_state.get('username')
    
    def get_user_role(self) -> Optional[str]:
        """Get current user role"""
        return st.session_state.get('role')
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get complete session information"""
        return {
            'user_id': st.session_state.get('user_id'),
            'username': st.session_state.get('username'),
            'role': st.session_state.get('role'),
            'authenticated': st.session_state.get('authenticated', False),
            'login_time': st.session_state.get('login_time'),
            'last_activity': st.session_state.get('last_activity'),
            'current_project': st.session_state.get('current_project'),
            'session_duration': self._get_session_duration(),
            'time_remaining': self._get_time_remaining()
        }
    
    def _get_session_duration(self) -> Optional[float]:
        """Get session duration in minutes"""
        login_time = st.session_state.get('login_time')
        if not login_time:
            return None
        
        return (datetime.now() - login_time).total_seconds() / 60
    
    def _get_time_remaining(self) -> Optional[float]:
        """Get time remaining until session timeout in minutes"""
        last_activity = st.session_state.get('last_activity')
        if not last_activity:
            return None
        
        elapsed = (datetime.now() - last_activity).total_seconds() / 60
        return max(0, self.session_timeout_minutes - elapsed)
    
    def update_activity(self):
        """Update last activity timestamp"""
        st.session_state.last_activity = datetime.now()
    
    def set_current_project(self, project_name: str):
        """Set current active project"""
        st.session_state.current_project = project_name
        self.update_activity()
    
    def get_current_project(self) -> Optional[str]:
        """Get current active project"""
        return st.session_state.get('current_project')
    
    def set_current_page(self, page_name: str):
        """Set current page for navigation highlighting"""
        st.session_state.current_page = page_name
        self.update_activity()
    
    def get_current_page(self) -> Optional[str]:
        """Get current page"""
        return st.session_state.get('current_page')
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if current user has specific permission
        
        Args:
            permission: Permission to check
            
        Returns:
            bool: True if user has permission
        """
        from .permissions import check_permission
        return check_permission(st.session_state.get('role'), permission)
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return st.session_state.get('role') == 'Admin'
    
    def is_manager(self) -> bool:
        """Check if current user is manager or admin"""
        role = st.session_state.get('role')
        return role in ['Directeur', 'Admin']
    
    def get_session_timeout_warning(self) -> Optional[Dict[str, Any]]:
        """
        Get session timeout warning information
        
        Returns:
            Dict with warning info if session is about to expire, None otherwise
        """
        time_remaining = self._get_time_remaining()
        
        if time_remaining and time_remaining <= 5:  # 5 minutes remaining
            return {
                'minutes_remaining': round(time_remaining, 1),
                'message': f"Votre session expirera dans {round(time_remaining, 1)} minutes",
                'severity': 'warning' if time_remaining > 1 else 'error'
            }
        
        return None
    
    def get_user(self) -> Optional[Dict]:
        """Backward compatibility method for old code"""
        if not self.is_authenticated():
            return None
    
        return {
        'id': self.get_user_id(),
        'username': self.get_username(), 
        'role': self.get_user_role(),
        'full_name': st.session_state.get('user', {}).get('full_name', '')
        }

    @property
    def user(self) -> Optional[Dict]:
        """Property access for backward compatibility"""
        return self.get_user()