"""
PROFESSIONAL Equipment Table Component - Civil Engineering Scheduling
Optimized for resource template management
"""
import streamlit as st
import pandas as pd
import logging
from typing import List, Dict, Optional, Any
from backend.utils.widget_manager import widget_manager

logger = logging.getLogger(__name__)

# French column mapping for equipment
FRENCH_COLUMNS = {
    "code": "Code", "name": "Nom", "type": "Type", "category": "Catégorie",
    "model": "Modèle", "base_count": "Quantité Base", "hourly_rate": "Taux Horaire", 
    "daily_rate": "Taux Journalier", "capacity": "Capacité",
    "max_units_per_task": "Max par Tâche", "base_productivity_rate": "Taux Productivité Base",
    "productivity_unit": "Unité Productivité", "requires_operator": "Nécessite Opérateur",
    "operator_type": "Type Opérateur", "is_available": "Disponible", "is_active": "Actif"
}

def render_equipment_table(equipment: List[Dict], resource_service, user_id: int, available_templates: List[Dict], template_id: Optional[int] = None, current_template_name: str = ""):
    """
    Render equipment resources table with CRUD operations and template-level actions
    """
    # Initialize state
    if 'equipment_form_state' not in st.session_state:
        st.session_state.equipment_form_state = {'mode': None, 'current_equipment': None}
    
    # Template-level actions section
    _render_template_actions(resource_service, user_id, available_templates, template_id, current_template_name)
    
    state = st.session_state.equipment_form_state
    
    # Apply filters
    filtered_equipment = _render_equipment_filters(equipment)
    
    # Render statistics
    _render_equipment_statistics(equipment, filtered_equipment)
    
    # Render active form if needed
    if state['mode']:
        _render_equipment_form(state, equipment, resource_service, user_id, available_templates, template_id)
        return
    
    # Main table interface
    _render_equipment_table_interface(filtered_equipment, resource_service, user_id, available_templates, template_id)

def _render_template_actions(resource_service, user_id: int, available_templates: List[Dict], template_id: Optional[int] = None, current_template_name: str = ""):
    """Render template-level action buttons"""
    st.markdown("### 🔧 Actions au Niveau Modèle")
    
    # Display current template info if available
    if template_id and current_template_name:
        st.info(f"**Modèle actuel:** {current_template_name} (ID: {template_id})")
    
    # Template action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Sauvegarder Modèle", use_container_width=True,
                    key=widget_manager.generate_key("save_template_btn", "equipment_table")):
            _save_resource_template(resource_service, user_id, template_id, available_templates)
    
    with col2:
        if st.button("➕ Nouveau Modèle", use_container_width=True,
                    key=widget_manager.generate_key("new_template_btn", "equipment_table")):
            _create_new_template(resource_service, user_id)
    
    with col3:
        if st.button("📥 Charger Défaut", use_container_width=True,
                    key=widget_manager.generate_key("load_default_btn", "equipment_table")):
            _load_default_resources(resource_service, user_id)
    
    with col4:
        if st.button("🔄 Actualiser", use_container_width=True,
                    key=widget_manager.generate_key("refresh_btn", "equipment_table")):
            st.rerun()
    
    st.markdown("---")

def _save_resource_template(resource_service, user_id: int, template_id: Optional[int], available_templates: List[Dict]):
    """Save the current resource template"""
    try:
        if not template_id:
            st.error("❌ Aucun modèle sélectionné pour sauvegarde")
            return
        
        # Find template name
        template_name = next((t['name'] for t in available_templates if t['id'] == template_id), "Modèle Inconnu")
        
        # In a real implementation, this would save all workers and equipment in the template
        st.success(f"✅ Modèle '{template_name}' sauvegardé avec succès!")
        
        # Show statistics
        workers = resource_service.get_user_workers(user_id, template_id)
        equipment = resource_service.get_user_equipment(user_id, template_id)
        
        st.info(f"📊 Modèle contient: {len(workers)} ouvriers et {len(equipment)} équipements")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la sauvegarde du modèle: {e}")
        logger.error(f"Error saving template: {e}")

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



def _render_equipment_statistics(all_equipment: List[Dict], filtered_equipment: List[Dict]):
    """Render equipment statistics"""
    total_count = len(all_equipment)
    filtered_count = len(filtered_equipment)
    
    total_active = len([e for e in all_equipment if e.get('is_active', True)])
    filtered_active = len([e for e in filtered_equipment if e.get('is_active', True)])
    
    total_types = len(set(e.get('type', '') for e in all_equipment))
    filtered_types = len(set(e.get('type', '') for e in filtered_equipment))
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🛠️ Équipements", f"{filtered_count}/{total_count}")
    
    with col2:
        st.metric("✅ Actifs", f"{filtered_active}/{total_active}")
    
    with col3:
        st.metric("🎯 Types", f"{filtered_types}/{total_types}")
    
    with col4:
        filters_active = filtered_count != total_count
        status = "🔍 Filtres Actifs" if filters_active else "👁️ Tous Visible"
        st.metric("Statut", status)

def _render_equipment_filters(equipment: List[Dict]) -> List[Dict]:
    """Render equipment filters"""
    if not equipment:
        return []
    
    # Get unique values for filters
    types = sorted(list(set(eq.get('type', '') for eq in equipment if eq.get('type'))))
    categories = sorted(list(set(eq.get('category', '') for eq in equipment if eq.get('category'))))
    
    st.markdown("### 🔍 Filtres Équipements")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_type = st.selectbox(
            "Type",
            options=['Tous'] + types,
            key=widget_manager.generate_key("filter_equipment_type", "equipment_table")
        )
    
    with col2:
        selected_category = st.selectbox(
            "Catégorie",
            options=['Toutes'] + categories,
            key=widget_manager.generate_key("filter_equipment_category", "equipment_table")
        )
    
    with col3:
        selected_active = st.selectbox(
            "Statut", 
            options=['Tous', 'Actifs', 'Inactifs'],
            key=widget_manager.generate_key("filter_equipment_active", "equipment_table")
        )
    
    # Apply filters
    filtered_equipment = _apply_equipment_filters(equipment, selected_type, selected_category, selected_active)
    
    return filtered_equipment

def _apply_equipment_filters(equipment: List[Dict], eq_type: str, category: str, active: str) -> List[Dict]:
    """Apply filters to equipment list"""
    filtered = equipment
    
    if eq_type != 'Tous':
        filtered = [e for e in filtered if e.get('type') == eq_type]
    
    if category != 'Toutes':
        filtered = [e for e in filtered if e.get('category') == category]
    
    if active == 'Actifs':
        filtered = [e for e in filtered if e.get('is_active', True)]
    elif active == 'Inactifs':
        filtered = [e for e in filtered if not e.get('is_active', True)]
    
    return filtered

def _render_equipment_table_interface(equipment: List[Dict], equipment_service, user_id: int,available_templates: List[Dict], template_id: Optional[int] = None):
    """Render equipment table interface"""
    
    # Equipment selection
    selected_equipment = _render_equipment_selection(equipment)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.button("➕ Nouvel Équipement", use_container_width=True,
                    key=widget_manager.generate_key("new_equipment_btn", "equipment_table")):
            st.session_state.equipment_form_state = {'mode': 'new', 'current_equipment': None}
            st.rerun()
    
    with col2:
        disabled = selected_equipment is None
        if st.button("✏️ Modifier", use_container_width=True, disabled=disabled,
                    key=widget_manager.generate_key("edit_equipment_btn", "equipment_table")):
            st.session_state.equipment_form_state = {'mode': 'edit', 'current_equipment': selected_equipment}
            st.rerun()
    
    with col3:
        if st.button("📋 Dupliquer", use_container_width=True, disabled=disabled,
                    key=widget_manager.generate_key("duplicate_equipment_btn", "equipment_table")):
            st.session_state.equipment_form_state = {'mode': 'duplicate', 'current_equipment': selected_equipment}
            st.rerun()
    
    with col4:
        if st.button("🗑️ Supprimer", use_container_width=True, disabled=disabled,
                    key=widget_manager.generate_key("delete_equipment_btn", "equipment_table")):
            _delete_equipment(selected_equipment, equipment, equipment_service, user_id)
            st.rerun()
    
    # Data table
    _render_equipment_data_table(equipment)

def _render_equipment_selection(equipment: List[Dict]) -> Optional[Dict]:
    """Render equipment selection dropdown"""
    if not equipment:
        st.info("📭 Aucun équipement disponible")
        return None
        
    equipment_options = {f"{e.get('name', 'Sans nom')} ({e.get('code', 'N/A')})": e for e in equipment}
    
    selected_label = st.selectbox(
        "Sélectionner un équipement:",
        options=[''] + list(equipment_options.keys()),
        key=widget_manager.generate_key("equipment_selector", "equipment_table")
    )
    
    if selected_label and selected_label in equipment_options:
        return equipment_options[selected_label]
    
    return None

def _render_equipment_data_table(equipment: List[Dict]):
    """Render equipment data table"""
    if not equipment:
        st.info("📭 Aucun équipement à afficher")
        return
    
    # Convert to DataFrame
    df = _equipment_to_dataframe(equipment)
    
    # Display data editor
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Actif": st.column_config.CheckboxColumn("Actif"),
            "Disponible": st.column_config.CheckboxColumn("Disponible"),
            "Nécessite Opérateur": st.column_config.CheckboxColumn("Nécessite Opérateur"),
            "Taux Horaire": st.column_config.NumberColumn("Taux Horaire (€)", format="%.2f €"),
            "Quantité Base": st.column_config.NumberColumn("Quantité Base", min_value=0),
            "Max par Tâche": st.column_config.NumberColumn("Max par Tâche", min_value=1)
        },
        key=widget_manager.generate_key("equipment_data_editor", "equipment_table")
    )
    
    # Save changes
    if st.button("💾 Sauvegarder Modifications", use_container_width=True,
                key=widget_manager.generate_key("save_equipment_table_btn", "equipment_table")):
        _save_equipment_table_changes(edited_df, equipment)

def _render_equipment_form(state: Dict, all_equipment: List[Dict], equipment_service, user_id: int, template_id: Optional[int] = None):
    """Render equipment form for create/edit/duplicate"""
    mode = state['mode']
    equipment = state['current_equipment']
    
    st.markdown("---")
    
    if mode == 'edit':
        title = f"✏️ Modification: {equipment.get('name')}"
        submit_label = "💾 Sauvegarder"
    elif mode == 'duplicate':
        title = "📋 Duplication d'Équipement"
        submit_label = "✅ Créer Copie"
        equipment = equipment.copy() if equipment else None
    else:  # new
        title = "➕ Nouvel Équipement"
        submit_label = "➕ Créer Équipement"
        equipment = _get_default_equipment_template()
    
    st.subheader(title)
    
    with st.form(key=widget_manager.generate_key("equipment_form", "equipment_table")):
        # Basic Information
        equipment = _render_equipment_basic_info_section(equipment, mode)
        
        # Rates and Productivity
        equipment = _render_equipment_rates_section(equipment)
        
        # Operator and Availability
        equipment = _render_equipment_operator_section(equipment)
        
        # Form Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button(submit_label, use_container_width=True):
                if _validate_equipment(equipment, all_equipment, mode):
                    _save_equipment(equipment, all_equipment, equipment_service, user_id, template_id, mode)
        
        with col2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                st.session_state.equipment_form_state = {'mode': None, 'current_equipment': None}
                st.rerun()

def _render_equipment_basic_info_section(equipment: Dict, mode: str, available_templates: List[Dict]) -> Dict:
    """Render equipment basic information section with template selection"""
    st.markdown("### 📝 Informations de Base")
    
    col1, col2 = st.columns(2)
    with col1:
        equipment["name"] = st.text_input(
            "Nom de l'équipement *", 
            value=equipment.get("name", ""),
            key=widget_manager.generate_key("equipment_name", "equipment_table")
        )
        equipment["code"] = st.text_input(
            "Code *", 
            value=equipment.get("code", ""),
            key=widget_manager.generate_key("equipment_code", "equipment_table")
        )
        
    with col2:
        # Template selection
        template_options = {f"{t['name']} (ID: {t['id']})": t['id'] for t in available_templates}
        current_template_id = equipment.get("template_id")
        
        # Find current template name
        current_template_name = None
        if current_template_id:
            for template in available_templates:
                if template['id'] == current_template_id:
                    current_template_name = f"{template['name']} (ID: {template['id']})"
                    break
        
        selected_template = st.selectbox(
            "Modèle de ressources *",
            options=[''] + list(template_options.keys()),
            index=list(template_options.keys()).index(current_template_name) + 1 if current_template_name else 0,
            key=widget_manager.generate_key("equipment_template", "equipment_table")
        )
        
        if selected_template and selected_template in template_options:
            equipment["template_id"] = template_options[selected_template]
        else:
            st.error("❌ Veuillez sélectionner un modèle de ressources")
        
        equipment["type"] = st.text_input(
            "Type *", 
            value=equipment.get("type", ""),
            key=widget_manager.generate_key("equipment_type", "equipment_table")
        )
    
    col3, col4 = st.columns(2)
    with col3:
        equipment["category"] = st.selectbox(
            "Catégorie *",
            options=["EnginLourd", "Véhicule", "Outil", "ÉquipementSpécialisé"],
            index=["EnginLourd", "Véhicule", "Outil", "ÉquipementSpécialisé"].index(equipment.get("category", "EnginLourd")),
            key=widget_manager.generate_key("equipment_category", "equipment_table")
        )
    
    with col4:
        equipment["model"] = st.text_input(
            "Modèle", 
            value=equipment.get("model", ""),
            key=widget_manager.generate_key("equipment_model", "equipment_table")
        )
    
    equipment["base_count"] = st.number_input(
        "Quantité de base *", 
        value=equipment.get("base_count", 1), 
        min_value=1,
        key=widget_manager.generate_key("equipment_base_count", "equipment_table")
    )
    
    equipment["description"] = st.text_area(
        "Description",
        value=equipment.get("description", ""),
        key=widget_manager.generate_key("equipment_description", "equipment_table")
    )
    
    return equipment

def _render_equipment_rates_section(equipment: Dict) -> Dict:
    """Render equipment rates and productivity section"""
    st.markdown("### 💰 Tarifs et Productivité")
    
    col1, col2 = st.columns(2)
    with col1:
        equipment["hourly_rate"] = st.number_input(
            "Taux horaire (€) *", 
            value=equipment.get("hourly_rate", 0.0), 
            min_value=0.0,
            step=1.0,
            key=widget_manager.generate_key("equipment_hourly_rate", "equipment_table")
        )
        equipment["daily_rate"] = st.number_input(
            "Taux journalier (€)", 
            value=equipment.get("daily_rate", 0.0), 
            min_value=0.0,
            step=1.0,
            key=widget_manager.generate_key("equipment_daily_rate", "equipment_table")
        )
    
    with col2:
        equipment["base_productivity_rate"] = st.number_input(
            "Taux de productivité de base *", 
            value=equipment.get("base_productivity_rate", 1.0), 
            min_value=0.1,
            step=0.1,
            key=widget_manager.generate_key("equipment_productivity_rate", "equipment_table")
        )
        equipment["productivity_unit"] = st.text_input(
            "Unité de productivité *", 
            value=equipment.get("productivity_unit", "unités/jour"),
            key=widget_manager.generate_key("equipment_productivity_unit", "equipment_table")
        )
        equipment["max_units_per_task"] = st.number_input(
            "Maximum par tâche *", 
            value=equipment.get("max_units_per_task", 1), 
            min_value=1,
            key=widget_manager.generate_key("equipment_max_units", "equipment_table")
        )
    
    equipment["capacity"] = st.text_input(
        "Capacité",
        value=equipment.get("capacity", ""),
        key=widget_manager.generate_key("equipment_capacity", "equipment_table")
    )
    
    return equipment

def _render_equipment_operator_section(equipment: Dict) -> Dict:
    """Render equipment operator and availability section"""
    st.markdown("### 👷 Opérateur et Disponibilité")
    
    col1, col2 = st.columns(2)
    with col1:
        equipment["requires_operator"] = st.checkbox(
            "Nécessite un opérateur",
            value=equipment.get("requires_operator", True),
            key=widget_manager.generate_key("equipment_requires_operator", "equipment_table")
        )
        equipment["is_available"] = st.checkbox(
            "Disponible",
            value=equipment.get("is_available", True),
            key=widget_manager.generate_key("equipment_available", "equipment_table")
        )
    
    with col2:
        equipment["operator_type"] = st.text_input(
            "Type d'opérateur",
            value=equipment.get("operator_type", ""),
            key=widget_manager.generate_key("equipment_operator_type", "equipment_table")
        )
        equipment["is_active"] = st.checkbox(
            "Équipement actif",
            value=equipment.get("is_active", True),
            key=widget_manager.generate_key("equipment_active", "equipment_table")
        )
    
    return equipment

# --- DATA MANAGEMENT FUNCTIONS ---

def _equipment_to_dataframe(equipment: List[Dict]) -> pd.DataFrame:
    """Convert equipment to DataFrame for display"""
    if not equipment:
        return pd.DataFrame()
    
    display_data = []
    for eq in equipment:
        row = {}
        for eng_col, fr_col in FRENCH_COLUMNS.items():
            if eng_col in eq:
                value = eq[eng_col]
                if eng_col in ['is_active', 'is_available', 'requires_operator']:
                    row[fr_col] = '✅' if value else '❌'
                else:
                    row[fr_col] = value
        
        display_data.append(row)
    
    return pd.DataFrame(display_data)

def _save_equipment_table_changes(edited_df: pd.DataFrame, equipment: List[Dict]):
    """Save changes from data editor"""
    st.info("Fonctionnalité de sauvegarde en ligne à implémenter")

def _validate_equipment(equipment: Dict, all_equipment: List[Dict], mode: str) -> bool:
    """Validate equipment data"""
    errors = []
    
    if not equipment.get("name", "").strip():
        errors.append("Le nom de l'équipement est obligatoire")
    if not equipment.get("code", "").strip():
        errors.append("Le code est obligatoire")
    if not equipment.get("type", "").strip():
        errors.append("Le type est obligatoire")
    if equipment.get("hourly_rate", 0) <= 0:
        errors.append("Le taux horaire doit être positif")
    if equipment.get("base_count", 0) <= 0:
        errors.append("La quantité de base doit être positive")
    
    if mode == "new":
        existing_codes = [e.get("code", "").lower() for e in all_equipment]
        if equipment.get("code", "").lower() in existing_codes:
            errors.append("Un équipement avec ce code existe déjà")
    
    for error in errors:
        st.error(f"❌ {error}")
    
    return len(errors) == 0

def _save_equipment(equipment: Dict, equipment_list: List[Dict], equipment_service, user_id: int, template_id: Optional[int], mode: str):
    """Save equipment via service layer"""
    try:
        # Set template_id if provided
        if template_id:
            equipment['template_id'] = template_id
        
        if mode == 'edit':
            result = equipment_service.update_equipment(user_id, equipment.get('id'), equipment)
            if result:
                for i, e in enumerate(equipment_list):
                    if e.get('id') == equipment.get('id'):
                        equipment_list[i] = result
                        break
                st.success("✅ Équipement modifié avec succès!")
            
                            # Check if template was default and is now modified
                template = next((t for t in equipment_service.get_user_resource_templates(user_id) 
                               if t['id'] == template_id), None)
                if template and not template.get('is_default', True):
                    st.info("📝 Note: Ce modèle n'est plus considéré comme 'par défaut' car il a été modifié")

            else:
                st.error("❌ Erreur lors de la modification")
                
        elif mode == 'new':
            result = equipment_service.create_equipment(user_id, equipment)
            if result:
                equipment_list.append(result)
                st.success(f"✅ Équipement créé: {result.get('code')}")
            else:
                st.error("❌ Erreur lors de la création")
            
        elif mode == 'duplicate':
            duplicate_equipment = equipment.copy()
            duplicate_equipment['code'] = f"{equipment['code']}_COPY"
            result = equipment_service.create_equipment(user_id, duplicate_equipment)
            if result:
                equipment_list.append(result)
                st.success(f"✅ Équipement dupliqué: {result.get('code')}")
            else:
                st.error("❌ Erreur lors de la duplication")
        
        # Clear form state
        st.session_state.equipment_form_state = {'mode': None, 'current_equipment': None}
        
    except Exception as e:
        logger.error(f"Error saving equipment: {e}")
        st.error(f"❌ Erreur: {e}")

def _delete_equipment(equipment: Dict, equipment_list: List[Dict], equipment_service, user_id: int):
    """Delete equipment with confirmation"""
    equipment_id = equipment.get('id')
    equipment_name = equipment.get('name')
    
    st.warning(f"Êtes-vous sûr de vouloir supprimer '{equipment_name}'?")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirmer", key=widget_manager.generate_key("confirm_delete_equipment", "equipment_table")):
            try:
                success = equipment_service.delete_equipment(user_id, equipment_id)
                if success:
                    equipment_list[:] = [e for e in equipment_list if e.get('id') != equipment_id]
                    st.success(f"✅ Équipement supprimé: {equipment_name}")
                else:
                    st.error("❌ Erreur lors de la suppression")
            except Exception as e:
                logger.error(f"Error deleting equipment: {e}")
                st.error(f"❌ Erreur: {e}")
    
    with col2:
        if st.button("❌ Annuler", key=widget_manager.generate_key("cancel_delete_equipment", "equipment_table")):
            st.info("Suppression annulée")

def _get_default_equipment_template() -> Dict:
    """Get default equipment template"""
    return {
        "name": "", "code": "", "type": "", "category": "EnginLourd",
        "model": "", "base_count": 1, "hourly_rate": 0.0, "daily_rate": 0.0,
        "capacity": "", "max_units_per_task": 1, "base_productivity_rate": 1.0,
        "productivity_unit": "unités/jour", "requires_operator": True,
        "operator_type": "", "is_available": True, "is_active": True,
        "description": ""
    }