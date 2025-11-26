# frontend/helpers/template_manager.py

"""
Helper functions for Template Manager
Resolves inconsistencies and provides common utilities
"""
import streamlit as st
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

def get_resource_counts(resource_service, template_id: int, db_session=None) -> Tuple[int, int]:
    """Get worker and equipment counts for a template - RESOLVES INCONSISTENCY"""
    try:
        # Use resource_service method directly instead of creating new service
        workers = resource_service.get_workers_by_template(template_id)
        equipment = resource_service.get_equipment_by_template(template_id)
        return len(workers), len(equipment)
    except Exception as e:
        logger.error(f"Error getting resource counts: {e}")
        return 0, 0

def ensure_default_template_selected(resource_service, user_id: int) -> Optional[int]:
    """Ensure a template is selected, defaulting to the first available one"""
    try:
        resource_templates = resource_service.get_user_resource_templates(user_id)
        
        if not resource_templates:
            return None
        
        # Initialize or get selected template ID
        selected_id = st.session_state.get('selected_resource_template_id')
        
        # Validate selected template exists
        if selected_id and any(t['id'] == selected_id for t in resource_templates):
            return selected_id
        else:
            # Select first template
            first_template_id = resource_templates[0]['id']
            st.session_state.selected_resource_template_id = first_template_id
            return first_template_id
            
    except Exception as e:
        logger.error(f"Error ensuring template selection: {e}")
        return None

def refresh_template_data(resource_service, user_id: int) -> Dict[str, Any]:
    """Refresh all template data and ensure proper selection"""
    try:
        resource_templates = resource_service.get_user_resource_templates(user_id)
        selected_template_id = ensure_default_template_selected(resource_service, user_id)
        
        # Get resources for selected template
        workers = []
        equipment = []
        if selected_template_id:
            workers = resource_service.get_user_workers(user_id, selected_template_id)
            equipment = resource_service.get_user_equipment(user_id, selected_template_id)
        
        return {
            'templates': resource_templates,
            'selected_template_id': selected_template_id,
            'workers': workers,
            'equipment': equipment
        }
        
    except Exception as e:
        logger.error(f"Error refreshing template data: {e}")
        return {'templates': [], 'selected_template_id': None, 'workers': [], 'equipment': []}
def validate_task_dependencies(task_template: Dict, resource_template_id: int, template_service) -> Dict[str, Any]:
    """Validate task dependencies against resource template"""
    try:
        return template_service.validate_task_template_dependencies(task_template, resource_template_id)
    except Exception as e:
        logger.error(f"Error validating dependencies: {e}")
        return {
            'is_valid': False,
            'missing_workers': [],
            'missing_equipment': [],
            'warnings': [f"Erreur de validation: {str(e)}"]
        }

def render_stats_cards(statistics: Dict[str, any]):
    """Render professional statistics cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{statistics.get('templates', 0)}</h3>
            <p>Modèles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{statistics.get('workers', 0)}</h3>
            <p>Ouvriers</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{statistics.get('equipment', 0)}</h3>
            <p>Équipements</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{statistics.get('active', 0)}</h3>
            <p>Actifs</p>
        </div>
        """, unsafe_allow_html=True)

def get_resource_counts(resource_service, template_id: int) -> tuple[int, int]:
    """Get worker and equipment counts for a template - FIXED"""
    try:
        workers = resource_service.get_workers_by_template(template_id)
        equipment = resource_service.get_equipment_by_template(template_id)
        return len(workers), len(equipment)
    except Exception as e:
        logger.error(f"Error getting resource counts: {e}")
        return 0, 0