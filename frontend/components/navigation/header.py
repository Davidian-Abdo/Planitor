
"""
Enhanced header components - FIXED VERSION
Fully compatible with unified session management
"""
import streamlit as st
from typing import List, Optional
from datetime import datetime

# --------------------------
# PAGE HEADER
# --------------------------
def render_page_header(
    title: str,
    description: str = "",
    icon: str = "🏗️",
    show_breadcrumbs: bool = True,
    breadcrumbs: Optional[List[str]] = None
) -> None:
    """
    Render professional page header compatible with new architecture
    """
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.markdown(f"<h1 style='margin:0'>{icon} {title}</h1>", unsafe_allow_html=True)
        if description:
            st.markdown(f"<p style='margin:0;color:#666'>{description}</p>", unsafe_allow_html=True)
    
    with col2:
        if show_breadcrumbs:
            render_breadcrumbs(breadcrumbs or [title])
    
    with col3:
        render_header_actions()
    
    st.markdown("---")

# --------------------------
# BREADCRUMBS
# --------------------------
def render_breadcrumbs(items: List[str]) -> None:
    """Render breadcrumb navigation"""
    if not items:
        return
    breadcrumb_html = "<nav style='padding:0.5rem 0; font-size:0.9rem; color:#666;'>"
    for i, item in enumerate(items):
        if i == len(items) - 1:
            breadcrumb_html += f"<strong>{item}</strong>"
        else:
            breadcrumb_html += f"{item} &rsaquo; "
    breadcrumb_html += "</nav>"
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

# --------------------------
# HEADER ACTIONS
# --------------------------
def render_header_actions() -> None:
    """Render quick actions in header"""
    col1, col2, col3 = st.columns(3)
    with col1:
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.caption(f"🕒 {current_time}")
    with col2:
        st.button("🔔", help="Notifications", key="notif_btn")
    with col3:
        if st.button("❓", help="Aide", key="help_btn"):
            st.info("🔧 Centre d'aide - Fonctionnalité à venir")

# --------------------------
# PROJECT SELECTOR IN HEADER
# --------------------------
def render_project_selector_header(db_session, user_id: int) -> None:
    """Project selector for header, integrated with session state"""
    from backend.services.project_service import ProjectService

    try:
        project_service = ProjectService(db_session)
        projects = project_service.get_user_projects(user_id)

        if projects:
            current_project = st.session_state.get("current_project")
            project_options = [f"🏗️ {p.name}" for p in projects]
            selected_project = st.selectbox(
                "Sélectionner un projet:",
                options=project_options,
                index=0 if not current_project else next(
                    (i for i, p in enumerate(projects) if p.name == current_project), 0
                ),
                label_visibility="collapsed"
            )
            if selected_project:
                project_name = selected_project.replace("🏗️ ", "")
                if project_name != current_project:
                    st.session_state.current_project = project_name
                    st.success(f"✅ Projet **{project_name}** activé")
                    st.rerun()
        else:
            st.warning("📝 Aucun projet disponible")
    except Exception:
        st.error("❌ Erreur sélection projet")

# --------------------------
# QUICK ACTION BUTTONS
# --------------------------
def render_quick_action_buttons(db_session, user_id: int) -> None:
    """Render quick action buttons in header"""
    st.markdown("### 🚀 Actions Rapides")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📥 Nouveau Projet", use_container_width=True):
            st.session_state.current_page = 'project_setup'
            st.rerun()
    with col2:
        if st.button("📊 Générer Planning", use_container_width=True):
            st.session_state.current_page = 'generate_schedule'
            st.rerun()
    with col3:
        if st.button("📈 Suivi Progression", use_container_width=True):
            st.session_state.current_page = 'progress_monitoring'
            st.rerun()
    with col4:
        if st.button("📄 Exporter Rapport", use_container_width=True):
            st.info("📋 Fonctionnalité d'export à venir")

# --------------------------
# SECTION INDICATOR
# --------------------------
def render_section_indicator(current_section: str) -> None:
    """Render visual indicator for current section"""
    if current_section == "scheduling":
        st.markdown(
            "<div style='background:linear-gradient(90deg,#e3f2fd,#bbdefb); padding:0.5rem; border-radius:0.5rem; text-align:center;'>"
            "<strong>📅 MODE PLANIFICATION</strong></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background:linear-gradient(90deg,#f3e5f5,#e1bee7); padding:0.5rem; border-radius:0.5rem; text-align:center;'>"
            "<strong>📊 MODE SUIVI & ANALYSE</strong></div>",
            unsafe_allow_html=True
        )

# --------------------------
# PROGRESS INDICATOR
# --------------------------
def render_progress_indicator(progress: float, label: str = "Progression") -> None:
    """Render progress indicator in header"""
    st.markdown(
        f"<div style='margin:0.5rem 0;'>"
        f"<div style='display:flex; justify-content:space-between; margin-bottom:0.2rem;'>"
        f"<span><strong>{label}</strong></span><span><strong>{progress:.1f}%</strong></span></div>"
        f"<div style='background:#f0f0f0; border-radius:10px; height:8px;'>"
        f"<div style='background:linear-gradient(90deg,#4CAF50,#8BC34A); width:{progress}%; height:100%; border-radius:10px;'></div>"
        f"</div></div>",
        unsafe_allow_html=True
    )