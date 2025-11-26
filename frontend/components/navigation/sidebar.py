"""
Enhanced sidebar navigation - FIXED VERSION
Fully compatible with unified session management
"""
import streamlit as st
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def render_main_sidebar(db_session, user_id: int, current_section: str = "scheduling") -> None:
    """
    FIXED Enhanced main sidebar with proper page switching
    """
    with st.sidebar:
        # Application Branding
        st.markdown(
            """
            <div style='text-align: center; padding: 1rem 0;'>
                <h1 style='margin: 0; color: #1f77b4;'>🏗️</h1>
                <h3 style='margin: 0; color: #333;'>Construction Planner</h3>
                <p style='margin: 0; font-size: 0.8rem; color: #666;'>Version Professionnelle</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("---")

        # User Profile Section
        render_user_profile(db_session, user_id)

        # Project Context Selector
        render_project_selector(db_session, user_id)

        # Section Navigation
        st.markdown("## 🧭 Navigation Principale")
        tab1, tab2 = st.tabs(["📅 Planification", "📊 Suivi"])

        with tab1:
            render_scheduling_navigation(db_session, user_id, current_section == "scheduling")
        with tab2:
            render_monitoring_navigation(db_session, user_id, current_section == "monitoring")

        # Quick Stats & Actions
        st.markdown("---")
        render_quick_stats(db_session, user_id)

        # System Status & Footer
        render_system_footer()

def render_user_profile(db_session, user_id: int) -> None:
    """FIXED Enhanced user profile"""
    try:
        # ✅ Use CORRECT session manager
        if 'auth_session_manager' not in st.session_state:
            st.error("❌ Authentication not initialized")
            return
            
        session_manager = st.session_state.auth_session_manager
        
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("<div style='text-align: center; font-size: 2rem;'>👤</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{session_manager.get_username()}**")
                st.caption(f"@{session_manager.get_username()} • {session_manager.get_user_role().upper()}")
                st.markdown(f"`User ID: {user_id}`")

    except Exception as e:
        logger.error(f"Error rendering user profile: {e}")
        st.error("❌ Erreur profil utilisateur")

def render_project_selector(db_session, user_id: int, page_title: str = "Navigation") -> None:
    """
    FIXED Professional Project Selector
    """
    try:
        from backend.services.project_service import ProjectService
        project_service = ProjectService(db_session)

        # Retrieve user projects
        projects = project_service.get_user_projects(user_id) or []

        if projects:
            # Prepare display names safely
            project_names = []
            for project in projects:
                name = getattr(project, 'name', project.get('name', 'Unnamed Project'))
                project_names.append(f"🏗️ {name}")

            selected_index = 0
            current_project_name = st.session_state.get('current_project_name')

            # Find index of currently selected project
            if current_project_name:
                for i, name in enumerate(project_names):
                    if current_project_name in name:
                        selected_index = i
                        break

            # Render the selectbox
            selected_project = st.selectbox(
                "📋 Projet Actif",
                options=project_names,
                index=selected_index,
                help="Sélectionnez le projet sur lequel travailler"
            )

            if selected_project:
                project_name_clean = selected_project.replace("🏗️ ", "")
                st.session_state.current_project_name = project_name_clean

                # Find project ID safely
                for project in projects:
                    pid = getattr(project, 'id', project.get('id', None))
                    pname = getattr(project, 'name', project.get('name', None))
                    if pname == project_name_clean:
                        st.session_state.current_project_id = pid
                        break

        else:
            st.info("📝 Aucun projet créé")
            if st.button("➕ Créer un Nouveau Projet", use_container_width=True):
                st.session_state.current_page = 'project_setup'
                st.rerun()

    except Exception as e:
        logger.error(f"Error in render_project_selector: {e}", exc_info=True)
        st.error(f"❌ Erreur chargement projets: {e}")

def render_scheduling_navigation(db_session, user_id: int, is_active: bool = True) -> None:
    """FIXED Render scheduling navigation with proper page switching"""
    st.markdown("### 📅 Planification")

    scheduling_pages: List[Dict[str, Any]] = [
        {"name": "🏗️ Configuration Projet", "page": "project_setup", "description": "Configuration initiale du projet et des zones", "icon": "🏗️"},
        {"name": "⚙️ Séquences de Travail", "page": "zone_sequence", "description": "Définition des séquences et dépendances", "icon": "⚙️"},
        {"name": "📊 Gestion Templates", "page": "templates_manager", "description": "Import et gestion des modèles Excel", "icon": "📊"},
        {"name": "📅 Génération Planning", "page": "generate_schedule", "description": "Génération et optimisation du planning", "icon": "📅"},
    ]

    for page in scheduling_pages:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"<h3>{page['icon']}</h3>", unsafe_allow_html=True)
            with col2:
                button_key = f"nav_sched_{user_id}_{page['page']}"
                
                if st.button(
                    page["name"],
                    key=button_key,
                    use_container_width=True,
                    type="primary" if st.session_state.get('current_page') == page['page'] else "secondary"
                ):
                    # ✅ FIXED: Set page in session state and trigger rerun
                    st.session_state.current_page = page['page']
                    st.session_state.navigation_section = "scheduling"
                    st.rerun()
                    
                st.caption(page["description"])

def render_monitoring_navigation(db_session, user_id: int, is_active: bool = True) -> None:
    """FIXED Enhanced monitoring navigation with proper page switching"""
    st.markdown("### 📊 Suivi & Analyse")

    monitoring_pages: List[Dict[str, Any]] = [
        {"name": "📈 Suivi Progression", "page": "progress_monitoring", "description": "Suivi temps réel de l'avancement", "icon": "📈"},
        {"name": "📋 Tableau de Bord", "page": "performance_dashboard", "description": "Indicateurs de performance et KPI", "icon": "📋"},
        {"name": "📄 Rapports & Analytics", "page": "reports_analytics", "description": "Rapports détaillés et analyses", "icon": "📄"},
    ]

    for page in monitoring_pages:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"<h3>{page['icon']}</h3>", unsafe_allow_html=True)
            with col2:
                button_key = f"nav_mon_{user_id}_{page['page']}"
                
                if st.button(
                    page["name"],
                    key=button_key,
                    use_container_width=True,
                    type="primary" if st.session_state.get('current_page') == page['page'] else "secondary"
                ):
                    # ✅ FIXED: Set page in session state and trigger rerun
                    st.session_state.current_page = page['page']
                    st.session_state.navigation_section = "monitoring"
                    st.rerun()
                    
                st.caption(page["description"])

def render_quick_stats(db_session, user_id: int) -> None:
    """FIXED Enhanced quick stats"""
    try:
        from backend.services.project_service import ProjectService
        project_service = ProjectService(db_session)
        projects = project_service.get_user_projects(user_id)

        # Project Statistics
        active_projects = len([p for p in projects if getattr(p, 'status', '') == 'active'])
        total_projects = len(projects)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Projets Actifs", active_projects)
        with col2:
            st.metric("Total Projets", total_projects)

    except Exception as e:
        logger.error(f"Error rendering quick stats: {e}")
        st.error(f"❌ Erreur statistiques: {e}")

def render_system_footer() -> None:
    """FIXED Enhanced system footer"""
    st.markdown("---")
    if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
        # ✅ Use CORRECT session manager
        if 'auth_session_manager' in st.session_state:
            st.session_state.auth_session_manager.logout()
            st.rerun()

    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0; color: #666; font-size: 0.8rem;'>
            <p>🏗️ <strong>Construction Planner Pro</strong></p>
            <p>Version 2.1.0 • © 2024</p>
        </div>
        """,
        unsafe_allow_html=True
    )