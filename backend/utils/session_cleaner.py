# backend/core/session_cleaner.py
"""
Centralized Session Cleaner for User Logout
"""
import streamlit as st
import logging
from typing import Set

logger = logging.getLogger(__name__)

class SessionCleaner:
    """Professional session state cleanup manager"""
    
    # Keys that should persist across users (app configuration)
    PERSISTENT_KEYS = {
        'app_initialized', 'widget_debug', 'widget_manager', 
        'auth_session_manager', '_pages'
    }
    
    # User-specific keys to clean on logout
    USER_SESSION_KEYS = {
        # Authentication
        'user_id', 'username', 'role', 'authenticated', 'login_time', 
        'last_activity', 'token', 'user',
        
        # Project data
        'current_project_id', 'current_project_name', 'current_project',
        'project_config', 'project_zones', 'project_sequences',
        
        # Schedule data
        'schedule_generated', 'schedule_results', 'selected_task_template',
        'selected_resource_template', 'input_method', 'reports_folder',
        
        # UI state
        'current_page', 'navigation_section', '_previous_page',
        
        # Uploads and caches
        'uploaded_files', 'file_cache', 'template_cache',
        
        # Form states
        'form_data', 'edit_mode', 'selected_items'
    }
    
    @classmethod
    def clean_user_session(cls, user_id: int = None) -> int:
        """
        Comprehensive user session cleanup
        Returns number of keys cleaned
        """
        cleaned_count = 0
        
        # Clean widget keys for user
        if user_id and 'widget_manager' in st.session_state:
            try:
                widget_manager = st.session_state.widget_manager
                if hasattr(widget_manager, 'cleanup_user_keys'):
                    keys_cleaned = widget_manager.cleanup_user_keys(str(user_id))
                    logger.info(f"Cleaned up {keys_cleaned} widget keys for user {user_id}")
            except Exception as e:
                logger.error(f"Error cleaning widget keys: {e}")
        
        # Clean user-specific session state
        for key in list(st.session_state.keys()):
            if key not in cls.PERSISTENT_KEYS and key in cls.USER_SESSION_KEYS:
                del st.session_state[key]
                cleaned_count += 1
                logger.debug(f"Cleaned session key: {key}")
        
        # Reset navigation to login
        st.session_state.current_page = 'login'
        st.session_state.navigation_section = 'scheduling'
        
        logger.info(f"Session cleanup completed: {cleaned_count} keys removed")
        return cleaned_count