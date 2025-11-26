"""
PROFESSIONAL Construction Project Planner - FIXED VERSION
Unified Session Management & Transaction Safety
"""

import streamlit as st
import logging
import sys
import os
from sqlalchemy.orm import Session
from typing import Optional, Callable,Dict,  Any
from contextlib import contextmanager

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConstructionApp:
    """
    FIXED Professional main application with unified session management
    """

    def __init__(self):
        self._setup_page_config()
        self._initialize_session_state()
        self._initialize_database()

    # ------------------- Initialization -------------------

    def _setup_page_config(self):
        """Setup professional page configuration"""
        st.set_page_config(
            page_title="Construction Project Planner",
            page_icon="🏗️",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo/construction-planner',
                'Report a bug': "https://github.com/your-repo/construction-planner/issues",
                'About': "### 🏗️ Construction Project Planner\nProfessional construction scheduling and resource management system"
            }
        )

    def _initialize_session_state(self):
        """Initialize unified session state"""
        # 1. Authentication Session Manager (User identity & permissions)
        if 'auth_session_manager' not in st.session_state:
            from backend.auth.session_manager import SessionManager
            st.session_state.auth_session_manager = SessionManager()
            logger.info("✅ Authentication session manager initialized")

        # 2. Application state defaults
        defaults = {
            'app_initialized': True,
            'current_page': 'login',
            'current_project_id': None,
            'current_project_name': None,
            'navigation_section': 'scheduling',
            '_previous_page': None,
            'widget_debug': False,
            'project_config': {
                'basic_info': {
                    'project_name': 'My Construction Project',
                    'project_manager': '',
                    'start_date': None,
                    'description': '',
                    'project_type': 'Commercial',
                    'client_name': '',
                    'location': ''
                },
                'zones': {},
                'advanced_settings': {
                    'work_hours_per_day': 8,
                    'acceleration_factor': 1.0,
                    'risk_allowance': 0.1
                }
            },
            'project_zones': {}
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def _initialize_database(self):
        """Initialize database connection professionally"""
        try:
            from backend.db.session import init_database
            init_database()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            st.warning("⚠️ Database connection unavailable - using session storage")

    # ------------------- Session Management -------------------

    def _is_authenticated(self) -> bool:
        """Check if user is authenticated via auth session manager"""
        auth_manager = st.session_state.auth_session_manager
        return hasattr(auth_manager, 'is_authenticated') and auth_manager.is_authenticated()

    def _get_current_user_id(self) -> Optional[int]:
        """Get current user ID safely via auth session manager"""
        if self._is_authenticated():
            return st.session_state.auth_session_manager.get_user_id()
        return None

    def _initialize_services(self, db_session: Session, user_id: int) -> Dict[str, Any]:
        """
        Initialize all services with the current database session
        These services are request-scoped and not stored in session state
        """
        try:
            from backend.services.project_service import ProjectService
            from backend.services.user_task_service import UserTaskService
            from backend.services.resource_service import ResourceService
            from backend.services.template_service import TemplateService
            from backend.services.zone_sequence_service import ZoneSequenceService
            from backend.services.scheduling_service import SchedulingService
            from backend.services.reporting_service import ReportingService
            from backend.services.monitoring_service import MonitoringService
            
            services = {
                'project_service': ProjectService(db_session),
                'task_service': UserTaskService(db_session),
                'resource_service': ResourceService(db_session),
                'template_service': TemplateService(db_session),
                'zone_sequence_service': ZoneSequenceService(db_session),
                'scheduling_service': SchedulingService(db_session),
                'reporting_service': ReportingService(db_session),
                'monitoring_service': MonitoringService(db_session),
            }
            
            logger.info("✅ Services initialized with request-scoped session")
            return services
            
        except Exception as e:
            logger.error(f"❌ Error initializing services: {e}")
            return {}
    


    @contextmanager
    def _database_session_scope(self):
        """
        Professional database transaction scope for entire page lifecycle
        Auto-commit on success, auto-rollback on exception
        """
        from backend.db.session import get_db_session, safe_commit, safe_rollback
        
        session = get_db_session()
        try:
            logger.debug("🎯 Starting page transaction scope")
            yield session
            # Commit on successful completion
            safe_commit(session, "Page transaction")
            logger.debug("✅ Page transaction completed successfully")
            
        except Exception as e:
            # Rollback on any exception
            safe_rollback(session, f"Page transaction failed: {str(e)}")
            logger.error(f"❌ Transaction rolled back due to error: {e}")
            raise
            
        finally:
            # Always close session
            try:
                session.close()
                logger.debug("🔒 Database session closed")
            except Exception as e:
                logger.error(f"❌ Error closing session: {e}")

    # ------------------- Page Routing -------------------

    def _route_to_page(self, db_session, services: Dict, user_id: int):
        """Route to current page with provided database session"""
        page = st.session_state.get('current_page', 'login')

        # Import all page modules
        from pages import login, project_setup, register
        from frontend.pages import (
            zone_sequence, templates_manager, 
            generate_schedule, progress_monitoring, 
            performance_dashboard, reports_analytics
        )

        # Map pages to their show functions with session
        page_mapping = {
            # Authentication Pages
            'login': lambda: login.show(),
            'register': lambda: register.show(),

            # Scheduling Section
            'project_setup': lambda: project_setup.show(db_session, services, user_id),
            'zone_sequence': lambda: zone_sequence.show(db_session, services, user_id),
            'templates_manager': lambda: templates_manager.show(db_session, services, user_id),
            'generate_schedule': lambda: generate_schedule.show(db_session, services, user_id),

            # Monitoring Section
            'progress_monitoring': lambda: progress_monitoring.show(db_session, services, user_id),
            'performance_dashboard': lambda: performance_dashboard.show(db_session, services, user_id),
            'reports_analytics': lambda: reports_analytics.show(db_session, services, user_id),
        }

        # Execute page function
        page_function = page_mapping.get(page, self._render_error_page)
        page_function()

    def _render_error_page(self):
        """Render error page for unknown routes"""
        st.error(f"❌ Page not found: {st.session_state.get('current_page')}")
        if st.button("🏠 Return to Home"):
            st.session_state.current_page = "project_setup"
            st.rerun()

    # ------------------- Interface Rendering -------------------

    def _render_authenticated_interface(self):
        """
        FIXED: Professional authenticated interface with unified session management
        """
        try:
            # Single database transaction for entire page lifecycle
            with self._database_session_scope() as db_session:
                # Get user context from auth session manager
                auth_manager = st.session_state.auth_session_manager
                user_id = auth_manager.get_user_id()
                username = auth_manager.get_username()
                user_role = auth_manager.get_user_role()

                logger.info(f"👤 Rendering interface for: {username} (ID: {user_id}, Role: {user_role})")

                # ✅ FIXED: Initialize services with current session (not stored)
                services = self._initialize_services(db_session, user_id)

                # Widget management
                if 'widget_manager' not in st.session_state:
                    from backend.utils.widget_manager import widget_manager
                    st.session_state.widget_manager = widget_manager
                
                widget_manager = st.session_state.widget_manager
                current_page = st.session_state.get('current_page', 'unknown')
                
                # Clean up previous page keys
                previous_page = st.session_state.get('_previous_page')
                if previous_page and previous_page != current_page:
                    widget_manager.cleanup_page_keys(previous_page)
                    logger.info(f"🔄 Cleaned up widget keys for previous page: {previous_page}")
                
                st.session_state._previous_page = current_page
                
                # Render interface components
                self._render_interface_components(db_session,  services, user_id, username, user_role)

        except Exception as e:
            logger.error(f"❌ Error in authenticated interface: {e}")
            self._show_error_page(e)

    def _render_interface_components(self, db_session, services: Dict, user_id: int, username: str, user_role: str):
        """Render all UI components with proper session context"""
        from frontend.components.navigation.sidebar import render_main_sidebar
        from frontend.components.navigation.header import render_page_header

        # -------------------
        # Render Sidebar with user context
        # -------------------
        render_main_sidebar(db_session, user_id, st.session_state.navigation_section)

        # -------------------
        # Render Main Content Header
        # -------------------
        current_page_name = st.session_state.get('current_page', 'Dashboard')
        render_page_header(
            title=current_page_name.replace('_', ' ').title(),
            description=f"User: {username} | Role: {user_role}",
            icon="📊",
            show_breadcrumbs=True,
            breadcrumbs=[current_page_name.replace('_', ' ').title()]
        )

        # -------------------
        # Render Page Content with database session
        # -------------------
        self._route_to_page(db_session, services,user_id)

    def _render_login_interface(self):
        """Render login page (no database session needed)"""
        try:
            from pages.login import show as show_login_page
            show_login_page()
        except Exception as e:
            logger.error(f"❌ Login page error: {e}")
            self._show_error_page(e)

    # ------------------- Error Handling -------------------

    def _show_error_page(self, error: Exception):
        """Professional error page with technical details"""
        st.error("""
        ❌ Application Error
        We encountered an unexpected error. Please:
        1. Refresh the page
        2. Check your internet connection
        3. Contact support if the issue persists
        """)
        with st.expander("Technical Details (For Support)"):
            st.code(f"Error Type: {type(error).__name__}\nError Message: {str(error)}")

        if st.button("🔄 Restart Application"):
            # Clear critical session state and rerun
            keys_to_keep = ['auth_session_manager', 'widget_manager']
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep:
                    del st.session_state[key]
            st.rerun()

    # ------------------- Utilities -------------------

    def _show_widget_debug_info(self):
        """Show widget debugging information (optional)"""
        if st.session_state.get('widget_debug'):
            with st.sidebar.expander("🔧 Widget Debug Info", expanded=False):
                if 'widget_manager' in st.session_state:
                    stats = st.session_state.widget_manager.get_registry_stats()
                    st.write(f"**Total Widget Keys:** {stats['total_keys']}")
                    st.write(f"**Active Pages:** {stats['pages']}")
                    st.write(f"**Users in Registry:** {stats['users']}")
                
                if st.button("Clear Widget Registry"):
                    if 'widget_key_registry' in st.session_state:
                        st.session_state.widget_key_registry = set()
                    if 'widget_key_context' in st.session_state:
                        st.session_state.widget_key_context = {}
                    st.rerun()

    # ------------------- Main Run Method -------------------

    def run(self):
        """Run the professional application with enhanced session management"""
        try:

            
            # Route based on authentication
            if self._is_authenticated():
                self._render_authenticated_interface()
            else:
                self._render_login_interface()
                
            # Optional debug information
            self._show_widget_debug_info()
                
        except Exception as e:
            logger.error(f"❌ Fatal application error: {e}")
            self._show_error_page(e)

# ------------------- Entry Point -------------------

if __name__ == "__main__":
    app = ConstructionApp()
    app.run()


    