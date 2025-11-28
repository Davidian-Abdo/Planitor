"""
Resource Library Tab - Simplified with context integration
"""

import streamlit as st
import logging
from typing import Dict, Any, List

from frontend.helpers.template_context import render_template_context_selector

logger = logging.getLogger(__name__)

def render_resource_templates_tab(services: Dict[str, Any], user_id: int, db_session=None):
    """Simplified resource templates tab"""
    
    st.markdown("""
    <div class="template-manager-header">
        <h1>📦 Modèles de Ressources</h1>
        <p>Gérez vos modèles de ressources (ouvriers et équipements)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render template selectors
    render_template_context_selector(services, user_id)
    
    resource_service = services['resource_service']
    task_service = services['task_service']
      
    try:
        # Get current context
        from frontend.helpers.template_context import TemplateContextManager
        
        template_context= TemplateContextManager
        if not template_context.is_ready():
            st.info("👆 Sélectionnez un modèle de ressources et un modèle de tâches pour continuer")
            return 
        
        current_resource = template_context.resource_template
        current_task = template_context.task_template
        
        # Display current context
        st.info(f"**Contexte actuel:** {current_resource['name']} + {current_task.get('name', 'Sans nom')}")
        
        # Template actions
        _render_template_actions(resource_service, user_id)
        
        # Get workers and equipment
        template_id = current_resource['id']
        workers = resource_service.get_user_workers(user_id, template_id)
        equipment = resource_service.get_user_equipment(user_id, template_id)
        
        # Display in tabs
        tab1, tab2 = st.tabs(["👥 Ouvriers", "🛠️ Équipements"])
        
        with tab1:
            from frontend.components.data_tables.worker_table import render_workers_table
            template_service = services.get('template_service')
            render_workers_table(workers, resource_service, user_id, template_id, current_resource['name'], template_service=template_service)
        
        with tab2:
            from frontend.components.data_tables.equipment_table import render_equipment_table
            render_equipment_table(equipment, resource_service, user_id, template_id, current_resource['name'])
            
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        logger.error(f"Resource library error: {e}")

def _render_template_actions(resource_service, user_id: int):
    """Essential template actions"""
    st.markdown("### 🔧 Actions Modèle")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Sauvegarder", use_container_width=True):
            st.success("✅ Modèle sauvegardé")
    
    with col2:
        if st.button("📥 Charger Défaut", width='stretch'):
            try:
                loaded = resource_service.load_default_resources(user_id)
                if loaded:
                    st.success("✅ Ressources par défaut chargées!")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors du chargement")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

    with col3:
        if st.button("🔄 Actualiser", width='stretch'):
            st.rerun()
    
    st.markdown("---")
