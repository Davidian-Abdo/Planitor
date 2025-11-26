"""
PROFESSIONAL Widget Key Management System
Enhanced with PROPER session state initialization
"""
import streamlit as st
import hashlib
import logging
from typing import Optional, Set, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class StableWidgetKeyManager:
    """
    Professional widget key manager with PROPER session state initialization
    """
    
    def __init__(self):
        # ✅ PROPERLY initialize ALL session state components
        self._initialize_key_registry()
    
    def _initialize_key_registry(self):
        """
        CRITICAL: Initialize ALL session state components
        This must be called in __init__ to ensure everything exists
        """
        # Initialize each component individually with safe defaults
        if 'widget_key_registry' not in st.session_state:
            st.session_state.widget_key_registry = set()
        
        if 'widget_key_context' not in st.session_state:
            st.session_state.widget_key_context = {}
            
        # ✅ THIS WAS MISSING - Initialize the counters dictionary
        if 'widget_key_counters' not in st.session_state:
            st.session_state.widget_key_counters = {}
    
    def generate_key(self, base_key: str, page_context: str = None, user_id: str = None) -> str:
        """
        Generate STABLE widget key with SAFE session state access
        """
        # ✅ ENSURE session state is initialized before accessing
        self._initialize_key_registry()
        
        # Create deterministic key components
        key_components = [
            str(base_key),
            str(page_context) if page_context else "global",
            str(user_id) if user_id else "anonymous"
        ]
        
        # Create stable fingerprint
        key_fingerprint = self._create_stable_fingerprint(key_components)
        
        # ✅ SAFE ACCESS: Counter key should now exist
        counter_key = f"{key_fingerprint}_counter"
        
        # Initialize counter if it doesn't exist
        if counter_key not in st.session_state.widget_key_counters:
            st.session_state.widget_key_counters[counter_key] = 0
        
        # Final key with counter for uniqueness
        final_key = f"widget_{key_fingerprint}_{st.session_state.widget_key_counters[counter_key]}"
        
        # Register the key (only if new)
        if final_key not in st.session_state.widget_key_registry:
            st.session_state.widget_key_registry.add(final_key)
            st.session_state.widget_key_context[final_key] = {
                'base_key': base_key,
                'page_context': page_context,
                'user_id': user_id,
                'fingerprint': key_fingerprint,
                'created_at': datetime.now().isoformat()
            }
        
        return final_key
    
    def _create_stable_fingerprint(self, components: list) -> str:
        """
        Create STABLE fingerprint from key components
        """
        key_string = "::".join(components)
        return hashlib.md5(key_string.encode()).hexdigest()[:12]
    
    def cleanup_page_keys(self, page_context: str):
        """
        Clean up keys for a specific page context
        """
        if not page_context:
            return
        
        # ✅ ENSURE session state is initialized
        self._initialize_key_registry()
            
        keys_to_remove = [
            key for key in st.session_state.widget_key_registry.copy()
            if st.session_state.widget_key_context.get(key, {}).get('page_context') == page_context
        ]
        
        for key in keys_to_remove:
            st.session_state.widget_key_registry.discard(key)
            if key in st.session_state.widget_key_context:
                del st.session_state.widget_key_context[key]
    
        
    def cleanup_user_keys(self, user_id: str) -> int:
        """
        Clean up all widget keys for a specific user
        
        This method removes all widget keys associated with a user when they log out,
        preventing memory leaks and ensuring clean session state. 
       """
        self._initialize_key_registry()
        
        if not user_id:
            return 0
        
        user_id_str = str(user_id)
        keys_to_remove = []
        
        # Find all keys for this user
        for key in st.session_state.widget_key_registry.copy():
            key_context = st.session_state.widget_key_context.get(key, {})
            if key_context.get('user_id') == user_id_str:
                keys_to_remove.append(key)
        
        # Remove keys and clean up counters
        for key in keys_to_remove:
            self._remove_key_with_counter_cleanup(key)
        
        logger.info(f"Cleaned up {len(keys_to_remove)} widget keys for user {user_id_str}")
        return len(keys_to_remove)
    
    def _remove_key_with_counter_cleanup(self, key: str):
        """Remove key and clean up associated counter if unused"""
        if key in st.session_state.widget_key_context:
            fingerprint = st.session_state.widget_key_context[key].get('fingerprint')
            del st.session_state.widget_key_context[key]
        
        st.session_state.widget_key_registry.discard(key)
        
        # Clean up counter if no other keys use this fingerprint
        if fingerprint:
            counter_key = f"{fingerprint}_counter"
            other_keys_exist = any(
                ctx.get('fingerprint') == fingerprint 
                for ctx in st.session_state.widget_key_context.values()
            )
            if not other_keys_exist and counter_key in st.session_state.widget_key_counters:
                del st.session_state.widget_key_counters[counter_key]

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get professional statistics about widget key usage"""
        # ✅ ENSURE session state is initialized
        self._initialize_key_registry()
        
        contexts = [
            ctx.get('page_context', 'global') 
            for ctx in st.session_state.widget_key_context.values()
        ]
        
        users = [
            ctx.get('user_id', 'anonymous') 
            for ctx in st.session_state.widget_key_context.values()
        ]
        
        return {
            'total_keys': len(st.session_state.widget_key_registry),
            'active_pages': list(set(contexts)),
            'active_users': list(set(users)),
            'key_distribution': {
                page: contexts.count(page) 
                for page in set(contexts)
            }
        }

# Global professional instance
widget_manager = StableWidgetKeyManager()