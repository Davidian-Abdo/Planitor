"""
PROFESSIONAL Template Association Tab
Associates resource templates with task templates for scheduling engine
"""
import streamlit as st
import logging
from typing import Dict, Any, List, Optional
from backend.utils.widget_manager import widget_manager

logger = logging.getLogger(__name__)


def render_template_associations_tab(services: Dict[str, Any], user_id: int, db_session=None):
    """
    Render template associations tab for linking resource templates with task templates
    """
    st.markdown("""
    <div class="template-manager-header">
        <h1>🔗 Associations Templates</h1>
        <p>Associez les modèles de ressources avec les modèles de tâches</p>
    </div>
    """, unsafe_allow_html=True)
    
    template_service = services['template_service']
    resource_service = services['resource_service']
    task_service = services['task_service']
    
    # Template-level actions
    _render_template_actions(resource_service, user_id)
    
    try:
        # Get available templates
        resource_templates = template_service.get_available_resource_templates(user_id)
        task_templates = task_service.get_user_task_templates(user_id)
        
        if not resource_templates:
            st.warning("📭 Aucun modèle de ressource disponible. Créez d'abord des modèles de ressources.")
            return
        
        if not task_templates:
            st.warning("📭 Aucun modèle de tâche disponible. Créez d'abord des modèles de tâches.")
            return
        
        # Display statistics
        _render_association_statistics(resource_templates, task_templates, template_service, user_id)
        
        # Main association interface
        _render_association_interface(resource_templates, task_templates, template_service, user_id)
        
        # Validation section
        _render_validation_section(resource_templates, task_templates, template_service, resource_service)
        
    except Exception as e:
        st.error(f"❌ Erreur dans les associations de templates: {e}")
        logger.error(f"Template associations error: {e}")
        
def _render_association_statistics(resource_templates: List[Dict], task_templates: List[Dict], template_service, user_id: int):
    """Render association statistics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Modèles Ressources", len(resource_templates))
    
    with col2:
        st.metric("📚 Modèles Tâches", len(task_templates))
    
    with col3:
        # Count associations
        total_associations = 0
        for rt in resource_templates:
            associations = template_service.get_template_associations(rt.get('id'))
            total_associations += len(associations)
        st.metric("🔗 Associations", total_associations)
    
    with col4:
        # Coverage percentage
        coverage = (total_associations / max(len(task_templates), 1)) * 100
        st.metric("📊 Couverture", f"{coverage:.1f}%")

def _render_association_interface(resource_templates: List[Dict], task_templates: List[Dict], template_service, user_id: int):
    """Render main association interface"""
    st.markdown("### 🔗 Interface d'Association")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Modèles de Ressources")
        selected_resource_template = _render_resource_template_selection(resource_templates)
    
    with col2:
        st.markdown("#### 📚 Tâches Disponibles")
        if selected_resource_template:
            _render_task_assignment_interface(selected_resource_template, task_templates, template_service, user_id)
        else:
            st.info("👈 Sélectionnez un modèle de ressource pour voir les tâches disponibles")

def _render_resource_template_selection(resource_templates: List[Dict]) -> Optional[Dict]:
    """Render resource template selection"""
    template_options = {f"{rt.get('name', 'Sans nom')} (ID: {rt.get('id')})": rt for rt in resource_templates}
    
    selected_label = st.selectbox(
        "Sélectionnez un modèle de ressource:",
        options=[''] + list(template_options.keys()),
        key=widget_manager.generate_key("resource_template_selector", "template_association")
    )
    
    if selected_label and selected_label in template_options:
        selected_template = template_options[selected_label]
        
        # Display template details
        with st.expander("📋 Détails du Modèle Sélectionné", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nom:** {selected_template.get('name')}")
                st.write(f"**Catégorie:** {selected_template.get('category', 'Non spécifiée')}")
                st.write(f"**Description:** {selected_template.get('description', 'Aucune')}")
            
            with col2:
                st.write(f"**Version:** {selected_template.get('version', 1)}")
                st.write(f"**Statut:** {'✅ Actif' if selected_template.get('is_active', True) else '❌ Inactif'}")
                st.write(f"**Partagé:** {'✅ Oui' if selected_template.get('is_shared', False) else '❌ Non'}")
        
        return selected_template
    
    return None

def _render_task_assignment_interface(selected_resource_template: Dict, task_templates: List[Dict], template_service, user_id: int):
    """Render task assignment interface for selected resource template"""
    resource_template_id = selected_resource_template.get('id')
    
    # Get current associations
    current_associations = template_service.get_template_associations(resource_template_id)
    current_task_ids = [assoc.get('task_template_id') for assoc in current_associations]
    
    # Group tasks by discipline for better organization
    tasks_by_discipline = {}
    for task in task_templates:
        discipline = task.get('discipline', 'Non classé')
        if discipline not in tasks_by_discipline:
            tasks_by_discipline[discipline] = []
        tasks_by_discipline[discipline] = task
    
    st.markdown("#### 🎯 Tâches Associées")
    
    # Display current associations
    if current_task_ids:
        st.success(f"✅ {len(current_task_ids)} tâche(s) associée(s) à ce modèle")
        
        for task_id in current_task_ids:
            task = next((t for t in task_templates if t.get('base_task_id') == task_id), None)
            if task:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{task.get('name')}**")
                    st.caption(f"Discipline: {task.get('discipline')} | Type: {task.get('resource_type')}")
                with col2:
                    st.write(f"Durée: {task.get('base_duration', 'N/A')}j")
                with col3:
                    if st.button("🗑️", key=f"remove_{task_id}_{resource_template_id}"):
                        template_service.remove_task_association(resource_template_id, task_id)
                        st.success(f"✅ Association supprimée: {task.get('name')}")
                        st.rerun()
    else:
        st.warning("⚠️ Aucune tâche associée à ce modèle de ressource")
    
    st.markdown("---")
    st.markdown("#### ➕ Ajouter des Associations")
    
    # Multi-select for adding associations
    available_tasks = [t for t in task_templates if t.get('base_task_id') not in current_task_ids]
    
    if available_tasks:
        task_options = {
            f"{t.get('name')} ({t.get('base_task_id')}) - {t.get('discipline')}": t.get('base_task_id') 
            for t in available_tasks
        }
        
        selected_tasks = st.multiselect(
            "Sélectionnez les tâches à associer:",
            options=list(task_options.keys()),
            key=widget_manager.generate_key("task_association_multiselect", "template_association")
        )
        
        if selected_tasks and st.button("🔗 Associer les Tâches Sélectionnées", use_container_width=True):
            selected_task_ids = [task_options[task] for task in selected_tasks]
            success_count = 0
            
            for task_id in selected_task_ids:
                if template_service.associate_task_template(resource_template_id, task_id):
                    success_count += 1
            
            if success_count > 0:
                st.success(f"✅ {success_count} tâche(s) associée(s) avec succès!")
                st.rerun()
            else:
                st.error("❌ Erreur lors de l'association des tâches")
    else:
        st.info("🎉 Toutes les tâches disponibles sont déjà associées à ce modèle!")

def _render_validation_section(resource_templates: List[Dict], task_templates: List[Dict], template_service, resource_service):
    """Render validation section for template associations"""
    st.markdown("---")
    st.markdown("### ✅ Validation des Associations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔍 Vérification des Dépendances")
        
        selected_validation_template = st.selectbox(
            "Sélectionnez un modèle à valider:",
            options=[''] + [f"{rt.get('name')} (ID: {rt.get('id')})" for rt in resource_templates],
            key=widget_manager.generate_key("validation_template_selector", "template_association")
        )
        
        if selected_validation_template:
            template_id = int(selected_validation_template.split("ID: ")[1].split(")")[0])
            associations = template_service.get_template_associations(template_id)
            
            if associations:
                st.success(f"✅ {len(associations)} association(s) trouvée(s)")
                
                # Validate each association
                validation_results = []
                for assoc in associations:
                    task_id = assoc.get('task_template_id')
                    task = next((t for t in task_templates if t.get('base_task_id') == task_id), None)
                    
                    if task:
                        # Check if resource template has the required resources
                        validation = _validate_task_dependencies(task, template_id, resource_service)
                        validation_results.append({
                            'task': task,
                            'validation': validation
                        })
                
                # Display validation results
                for result in validation_results:
                    task = result['task']
                    validation = result['validation']
                    
                    with st.expander(f"🔍 {task.get('name')}", expanded=False):
                        if validation['is_valid']:
                            st.success("✅ Tâche compatible avec le modèle de ressources")
                        else:
                            st.error("❌ Incompatibilités détectées")
                            
                            if validation['missing_workers']:
                                st.write("**Ouvriers manquants:**")
                                for worker in validation['missing_workers']:
                                    st.write(f" - {worker}")
                            
                            if validation['missing_equipment']:
                                st.write("**Équipements manquants:**")
                                for equipment in validation['missing_equipment']:
                                    st.write(f" - {equipment}")
                            
                            if validation['warnings']:
                                st.write("**Avertissements:**")
                                for warning in validation['warnings']:
                                    st.warning(warning)
            else:
                st.warning("⚠️ Aucune association à valider pour ce modèle")
    
    with col2:
        st.markdown("#### 📊 Rapport de Couverture")
        
        # Generate coverage report
        coverage_data = []
        for rt in resource_templates:
            associations = template_service.get_template_associations(rt.get('id'))
            coverage_percentage = (len(associations) / len(task_templates)) * 100 if task_templates else 0
            
            coverage_data.append({
                'Modèle': rt.get('name'),
                'Associations': len(associations),
                'Couverture': f"{coverage_percentage:.1f}%",
                'Statut': '✅ Bonne' if coverage_percentage > 50 else '⚠️ Faible' if coverage_percentage > 0 else '❌ Aucune'
            })
        
        if coverage_data:
            import pandas as pd
            df = pd.DataFrame(coverage_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📊 Aucune donnée de couverture disponible")

def _validate_task_dependencies(task: Dict, resource_template_id: int, template_service) -> Dict[str, Any]:
    """Validate task dependencies against resource template using template service"""
    try:
        return template_service.validate_task_template_dependencies(task, resource_template_id)
    except Exception as e:
        logger.error(f"Error validating task dependencies: {e}")
        return {
            'is_valid': False,
            'missing_workers': [],
            'missing_equipment': [],
            'warnings': [f"Erreur de validation: {str(e)}"]
        }
    

def _render_template_actions(resource_service, user_id: int):
    """Render template-level action buttons for association tab"""
    st.markdown("### 🔧 Actions au Niveau Modèle")
    
    # Template action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Sauvegarder Tous", use_container_width=True,
                    key=widget_manager.generate_key("save_all_templates_btn", "template_association")):
            _save_all_templates(resource_service, user_id)
    
    with col2:
        if st.button("➕ Nouveau Modèle", use_container_width=True,
                    key=widget_manager.generate_key("new_template_btn", "template_association")):
            _create_new_template(resource_service, user_id)
    
    with col3:
        if st.button("📥 Charger Défaut", use_container_width=True,
                    key=widget_manager.generate_key("load_default_btn", "template_association")):
            _load_default_resources(resource_service, user_id)
    
    with col4:
        if st.button("🔄 Actualiser", use_container_width=True,
                    key=widget_manager.generate_key("refresh_btn", "template_association")):
            st.rerun()
    
    st.markdown("---")

def _save_all_templates(resource_service, user_id: int):
    """Save all resource templates"""
    try:
        templates = resource_service.get_user_resource_templates(user_id)
        total_workers = 0
        total_equipment = 0
        
        for template in templates:
            workers = resource_service.get_user_workers(user_id, template['id'])
            equipment = resource_service.get_user_equipment(user_id, template['id'])
            total_workers += len(workers)
            total_equipment += len(equipment)
        
        st.success(f"✅ Tous les modèles sauvegardés!")
        st.info(f"📊 Total: {len(templates)} modèles, {total_workers} ouvriers, {total_equipment} équipements")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la sauvegarde: {e}")
        logger.error(f"Error saving all templates: {e}")

def _create_new_template(resource_service, user_id: int):
    """Create a new resource template"""
    try:
        # Generate unique template name
        template_count = len(resource_service.get_user_resource_templates(user_id))
        new_template_name = f"Nouveau Modèle {template_count + 1}"
        
        template_data = {
            'name': new_template_name,
            'description': 'Nouveau modèle de ressources créé automatiquement',
            'category': 'Custom',
            'user_id': user_id
        }
        
        new_template = resource_service.create_resource_template(user_id, template_data)
        
        if new_template:
            st.success(f"✅ Nouveau modèle créé: {new_template_name}")
            st.rerun()
        else:
            st.error("❌ Erreur lors de la création du modèle")
            
    except Exception as e:
        st.error(f"❌ Erreur lors de la création du modèle: {e}")
        logger.error(f"Error creating template: {e}")

def _load_default_resources(resource_service, user_id: int):
    """Load default resources"""
    try:
        with st.spinner("📥 Chargement des ressources par défaut..."):
            loaded_resources = resource_service.load_default_resources(user_id)
            
            if loaded_resources:
                st.success(f"✅ {len(loaded_resources)} ressources par défaut chargées avec succès!")
                st.rerun()
            else:
                st.error("❌ Erreur lors du chargement des ressources par défaut")
                
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des ressources: {e}")
        logger.error(f"Error loading default resources: {e}")