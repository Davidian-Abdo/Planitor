"""
FIXED Task Library Tab - Using optimized task table with resource selection
"""
import streamlit as st
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def render_task_library_tab(services: Dict[str, Any], user_id: int, db_session=None):
    """Render task library tab with optimized table and resource selection"""
    
    st.markdown("""
    <div class="template-manager-header">
        <h1>📚 Bibliothèque des Tâches</h1>
        <p>Gérez vos templates de tâches</p>
    </div>
    """, unsafe_allow_html=True)
    
    task_service = services.get('task_service')
    resource_service = services.get('resource_service')
    
    if not task_service:
        st.error("❌ Service des tâches non disponible")
        return
    
    try:
        # Get tasks from service
        tasks = task_service.get_user_task_templates(user_id)
        
        # Get available resources if service exists
        available_resources = {'workers': [], 'equipment': []}
        if resource_service:
            try:
                available_workers = resource_service.get_user_workers(user_id)
                available_equipment = resource_service.get_user_equipment(user_id)
                available_resources = {
                    'workers': available_workers,
                    'equipment': available_equipment
                }
            except Exception as e:
                st.warning(f"⚠️ Impossible de charger les ressources: {e}")
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Tâches", len(tasks))
        with col2:
            included_tasks = len([t for t in tasks if t.get('included', True)])
            st.metric("Tâches Incluses", included_tasks)
        with col3:
            disciplines = len(set(t.get('discipline', '') for t in tasks))
            st.metric("Disciplines", disciplines)
        with col4:
            quality_gates = len([t for t in tasks if t.get('quality_gate', False)])
            st.metric("Points Contrôle", quality_gates)
        
        # Use optimized task table WITH resource selection
        from frontend.components.data_tables.task_table import render_tasks_table
        template_service = services.get('template_service')
        render_tasks_table(tasks, task_service, user_id, available_resources, template_service)
        
        # Load Default Tasks Section
        st.markdown("---")
        st.markdown("## 📥 Tâches par Défaut")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Chargez les tâches par défaut pour commencer rapidement")
        with col2:
            if st.button("📥 Charger Tâches Défaut", key="load_default_tasks_main"):
                try:
                    loaded = task_service.load_default_tasks(user_id)
                    if loaded:
                        st.success("✅ Tâches par défaut chargées!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors du chargement")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

    except Exception as e:
        st.error(f"❌ Erreur dans la bibliothèque des tâches: {e}")
        logger.error(f"Task library error: {e}")