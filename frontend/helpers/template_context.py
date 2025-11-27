"""
FIXED Template Context Manager with LAZY initialization
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import logging

logger = logging.getLogger(__name__)

class TemplateContextManager:
    """
    FIXED: Lazy template context manager that doesn't access session state on import
    """
    
    def __init__(self):
        self._observers: List[Callable] = []
        # ✅ REMOVE initialization from __init__ - do it lazily
    
    def _ensure_initialized(self):
        """Ensure template context is initialized in session state - LAZY"""
        if 'template_context' not in st.session_state:
            st.session_state.template_context = {
                'resource_template': None,
                'task_template': None,
                'last_updated': None,
                'initialized': False
            }
            logger.info("✅ Template context initialized in session state")
    
    @property
    def resource_template(self) -> Optional[Dict[str, Any]]:
        self._ensure_initialized()  # ✅ Initialize only when accessed
        return st.session_state.template_context['resource_template']
    
    @resource_template.setter
    def resource_template(self, template: Optional[Dict[str, Any]]):
        self._ensure_initialized()  # ✅ Initialize only when accessed
        st.session_state.template_context['resource_template'] = template
        st.session_state.template_context['last_updated'] = 'resource'
        self._notify_observers()
    
    @property
    def task_template(self) -> Optional[Dict[str, Any]]:
        self._ensure_initialized()  # ✅ Initialize only when accessed
        return st.session_state.template_context['task_template']
    
    @task_template.setter
    def task_template(self, template: Optional[Dict[str, Any]]):
        self._ensure_initialized()  # ✅ Initialize only when accessed
        st.session_state.template_context['task_template'] = template
        st.session_state.template_context['last_updated'] = 'task'
        self._notify_observers()
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get complete context with validation state"""
        self._ensure_initialized()  # ✅ Initialize only when accessed
        
        context = {
            'resource_template': self.resource_template,
            'task_template': self.task_template,
            'is_ready': bool(self.resource_template and self.task_template),
            'last_updated': st.session_state.template_context.get('last_updated'),
            'initialized': st.session_state.template_context.get('initialized', False)
        }
        
        # Add compatibility info if both templates are selected
        if context['is_ready']:
            context['compatibility'] = self._get_compatibility_summary()
            
        return context
    
    def is_ready(self) -> bool:
        """Check if both resource and task templates are set."""
        self._ensure_initialized()  # ✅ Initialize only when accessed
        return bool(self.resource_template and self.task_template)
    
    def initialize_with_services(self, services: Dict[str, Any], user_id: int):
        """Initialize context with services from app.py"""
        self._ensure_initialized()  # ✅ Initialize only when accessed
        
        try:
            if st.session_state.template_context.get('initialized'):
                return
                
            # Get available templates from services
            resource_service = services['resource_service']
            task_service = services['task_service']
            
            resource_templates = resource_service.get_user_resource_templates(user_id)
            task_templates = task_service.get_user_task_templates(user_id)
            
            # Set default selections if available
            if resource_templates:
                self.resource_template = resource_templates[0]
            
            if task_templates:
                # Use the first task template group
                task_groups = task_service.get_task_template_groups(user_id)
                if task_groups:
                    self.task_template = task_groups[0]
            
            st.session_state.template_context['initialized'] = True
            logger.info("✅ Template context initialized with services")
            
        except Exception as e:
            logger.error(f"❌ Error initializing template context with services: {e}")
    
    # ... rest of the methods remain the same ...

# Global instance - but it won't initialize session state until first access
template_context = TemplateContextManager()

def get_template_context() -> TemplateContextManager:
    """Get the global template context instance"""
    return template_context

def render_template_context_selector(services: Dict[str, Any], user_id: int):
    """
    Render template context selector component - UPDATED with safe access
    """
    context = get_template_context()
    
    # Initialize context with services if not done
    current_context = context.get_current_context()  # ✅ This will initialize if needed
    if not current_context['initialized']:
        context.initialize_with_services(services, user_id)
    
    st.markdown("### 🎯 Contexte de Travail")
    
    col1, col2 = st.columns(2)
    
    with col1:
        _render_resource_template_selector(services, user_id, context)
    
    with col2:
        _render_task_template_selector(services, user_id, context)
    
    # Display current context status
    _render_context_status(context, services)

def _render_resource_template_selector(services, user_id: int, context: TemplateContextManager):
    """Render resource template selector - UPDATED"""
    resource_service = services['resource_service']
    resource_templates = resource_service.get_user_resource_templates(user_id)
    
    if resource_templates:
        template_options = {f"{rt['name']} (ID: {rt['id']})": rt for rt in resource_templates}
        
        # Get current selection
        current_template = context.resource_template
        current_key = None
        if current_template:
            current_key = f"{current_template['name']} (ID: {current_template['id']})"
        
        selected_key = st.selectbox(
            "📦 Modèle de Ressources Actif:",
            options=[''] + list(template_options.keys()),
            index=list(template_options.keys()).index(current_key) + 1 if current_key else 0,
            key="resource_context_selector_main",
            help="Sélectionnez le modèle de ressources que vous modifiez"
        )
        
        if selected_key and selected_key in template_options:
            context.resource_template = template_options[selected_key]
        elif not selected_key:
            context.resource_template = None
            
    else:
        st.error("❌ Aucun modèle de ressources disponible")
        if st.button("📥 Créer Modèle Défaut", key="create_default_resource"):
            resource_service.load_default_resources(user_id)
            st.rerun()

def _render_task_template_selector(services, user_id: int, context: TemplateContextManager):
    """Render task template selector - UPDATED to use services from app.py"""
    task_service = services['task_service']
    
    # Get task template groups using the service method
    task_groups = task_service.get_task_template_groups(user_id)
    
    if task_groups:
        # Create display options for template groups
        template_options = {}
        for group in task_groups:
            template_name = group['template_name']
            disciplines = ', '.join(sorted(group['disciplines']))
            display_name = f"{template_name} ({group['task_count']} tâches, {disciplines})"
            template_options[display_name] = group
        
        # Get current selection
        current_template = context.task_template
        current_key = None
        if current_template:
            current_template_name = current_template.get('template_name')
            if current_template_name:
                for display_name, template_data in template_options.items():
                    if template_data['template_name'] == current_template_name:
                        current_key = display_name
                        break
        
        selected_key = st.selectbox(
            "📚 Groupe de Tâches Actif:",
            options=[''] + list(template_options.keys()),
            index=list(template_options.keys()).index(current_key) + 1 if current_key else 0,
            key="task_context_selector_main",
            help="Sélectionnez un groupe de tâches (template) pour les taux de productivité"
        )
        
        if selected_key and selected_key in template_options:
            context.task_template = template_options[selected_key]
        elif not selected_key:
            context.task_template = None
            
    else:
        st.error("❌ Aucun groupe de tâches disponible")
        if st.button("📥 Charger Tâches Défaut", key="load_default_tasks"):
            task_service.load_default_tasks(user_id)
            st.rerun()

def _render_context_status(context: TemplateContextManager, services: Dict[str, Any]):
    """Render current context status - UPDATED"""
    current_context = context.get_current_context()
    
    if current_context['is_ready']:
        st.success("✅ Contexte prêt pour les opérations")
        
        # Display template details
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Ressources:** {current_context['resource_template']['name']}")
        with col2:
            template_name = current_context['task_template'].get('template_name', 'Sans nom')
            st.info(f"**Tâches:** {template_name}")
        
        # Validate compatibility
        if st.button("🔍 Valider Compatibilité", key="validate_compatibility"):
            _validate_template_compatibility(context, services)
    else:
        st.warning("⚠️ Sélectionnez un modèle de ressources ET un modèle de tâches")

def _validate_template_compatibility(context: TemplateContextManager, services: Dict[str, Any]):
    """Validate template compatibility - UPDATED"""
    try:
        template_service = services['template_service']
        current_context = context.get_current_context()
        
        if current_context['is_ready']:
            validation = template_service.validate_template_compatibility(
                current_context['resource_template'],
                current_context['task_template']
            )
            
            if validation.get('compatible', False):
                st.success("✅ Templates compatibles!")
            else:
                st.error("❌ Problèmes de compatibilité détectés")
                
            # Show detailed validation results
            with st.expander("📋 Détails de Validation", expanded=True):
                st.json(validation)
                
    except Exception as e:
        st.error(f"❌ Erreur lors de la validation: {e}")