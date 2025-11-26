# frontend/components/data_tables/resource_template_table.py

"""
PROFESSIONAL Resource Template Table Component - UNIFIED RESOURCE MANAGEMENT
Enhanced for French Construction Planning with Row Actions
"""
import streamlit as st
import pandas as pd
import json
import pandas as pd
from typing import List, Dict, Optional, Any
from backend.utils.widget_manager import widget_manager

# French column mapping for Resource Templates
RESOURCE_TEMPLATE_FRENCH_COLUMNS = {
    "name": "Nom",
    "description": "Description", 
    "category": "Catégorie",
    "version": "Version",
    "worker_count": "Nb Ouvriers",
    "equipment_count": "Nb Équipements",
    "is_default": "Par Défaut",
    "is_shared": "Partagé",
    "is_active": "Actif"
}

def _apply_css_styles():
    """Apply enhanced CSS styles for resource templates"""
    st.markdown("""
    <style>
        .resource-template-header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 24px;
            border-left: 5px solid #ff6b35;
        }
        .resource-template-action-buttons {
            display: flex;
            gap: 8px;
            margin: 10px 0;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #ff6b35;
        }
        .resource-template-form-section {
            background: #fff3e0;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .template-row-actions {
            display: flex;
            gap: 5px;
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)

def _get_default_resource_template() -> Dict:
    """Get default resource template"""
    return {
        "name": "",
        "description": "",
        "category": "Default",
        "version": 1,
        "is_default": False,
        "is_shared": False,
        "is_active": True
    }

def _get_french_dataframe(templates: List[Dict], resource_service) -> pd.DataFrame:
    """Convert resource templates to French-labeled DataFrame with counts"""
    if not templates:
        return pd.DataFrame()
    
    try:
        # Enhance templates with resource counts
        enhanced_templates = []
        for template in templates:
            enhanced_template = template.copy()
            # Get resource counts
            workers = resource_service.get_workers_by_template(template['id'])
            equipment = resource_service.get_equipment_by_template(template['id'])
            enhanced_template['worker_count'] = len(workers)
            enhanced_template['equipment_count'] = len(equipment)
            enhanced_templates.append(enhanced_template)
        
        df = pd.DataFrame(enhanced_templates)
        
        # Rename columns to French
        rename_mapping = {eng_col: fr_col for eng_col, fr_col in RESOURCE_TEMPLATE_FRENCH_COLUMNS.items() if eng_col in df.columns}
        df_display = df.rename(columns=rename_mapping)
        
        # Format boolean columns
        bool_columns = ['Par Défaut', 'Partagé', 'Actif']
        for col in bool_columns:
            if col in df_display.columns:
                df_display[col] = df_display[col].map({True: "✅", False: "❌"})
        
        return df_display
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la création du tableau des modèles: {e}")
        return pd.DataFrame(templates) if templates else pd.DataFrame()

def render_resource_template_table(resource_templates: List[Dict], resource_service):
    """Render professional resource templates table with French UI and row actions"""
    _apply_css_styles()
    
    # Initialize session state for resource templates
    if "selected_resource_template" not in st.session_state:
        st.session_state.selected_resource_template = None
    if "editing_resource_template" not in st.session_state:
        st.session_state.editing_resource_template = None
    if "show_edit_resource_template_form" not in st.session_state:
        st.session_state.show_edit_resource_template_form = False
    if "show_new_resource_template_form" not in st.session_state:
        st.session_state.show_new_resource_template_form = False
    if "duplicating_template" not in st.session_state:
        st.session_state.duplicating_template = None
    
    # Add New Template Button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📦 Modèles de Ressources Unifiés")
    with col2:
        if st.button("➕ Nouveau Modèle", key="add_new_resource_template", use_container_width=True):
            st.session_state.show_new_resource_template_form = True
            st.rerun()
    
    # Conditional forms
    if st.session_state.show_edit_resource_template_form and st.session_state.editing_resource_template:
        _render_resource_template_form(st.session_state.editing_resource_template, resource_templates, resource_service, "edit")
    
    if st.session_state.show_new_resource_template_form:
        _render_resource_template_form(None, resource_templates, resource_service, "new")
    
    if st.session_state.duplicating_template:
        _render_duplicate_template_form(st.session_state.duplicating_template, resource_templates, resource_service)
    
    if not resource_templates:
        st.info("📦 Aucun modèle de ressources créé. Créez votre premier modèle unifié.")
        return

    # Display French table with row actions
    df_display = _get_french_dataframe(resource_templates, resource_service)
    if not df_display.empty:
        # Create a more interactive display with row actions
        for index, template in enumerate(resource_templates):
            _render_template_row(template, resource_service, index)
    else:
        st.info("Aucun modèle de ressources à afficher")

    # Template selection and actions
    _render_template_actions(resource_templates, resource_service)

def _render_template_row(template: Dict, resource_service, index: int):
    """Render a single template row with action buttons"""
    col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 2, 2, 2, 2, 2, 3])
    
    with col1:
        st.write(f"**{template.get('name', 'Sans nom')}**")
        st.caption(template.get('description', '')[:50] + "..." if len(template.get('description', '')) > 50 else template.get('description', ''))
    
    with col2:
        st.write(f"v{template.get('version', 1)}")
    
    with col3:
        st.write(template.get('category', 'Default'))
    
    with col4:
        workers_count = len(resource_service.get_workers_by_template(template['id']))
        st.write(f"👷 {workers_count}")
    
    with col5:
        equipment_count = len(resource_service.get_equipment_by_template(template['id']))
        st.write(f"🛠️ {equipment_count}")
    
    with col6:
        st.write("✅" if template.get('is_default', False) else "❌")
        st.write("✅" if template.get('is_shared', False) else "❌")
        st.write("✅" if template.get('is_active', True) else "❌")
    
    with col7:
        # Row action buttons
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("✏️", key=f"edit_template_{template['id']}_{index}", help="Modifier"):
                st.session_state.editing_resource_template = template
                st.session_state.show_edit_resource_template_form = True
                st.rerun()
        
        with action_col2:
            if st.button("📋", key=f"duplicate_template_{template['id']}_{index}", help="Dupliquer"):
                st.session_state.duplicating_template = template
                st.rerun()
        
        with action_col3:
            if st.button("🗑️", key=f"delete_template_{template['id']}_{index}", help="Supprimer"):
                _delete_resource_template(template, resource_service)
    
    st.markdown("---")

def _render_template_actions(templates: List[Dict], resource_service):
    """Render template selection and action buttons"""
    
    st.markdown('<div class="resource-template-action-buttons">', unsafe_allow_html=True)
    
    # Build template options for dropdown
    template_options = {}
    default_index = 0
    
    for t in templates:
        template_id = t.get("id", "N/A")
        template_name = t.get("name", "Sans nom")
        template_options[f"{template_name} (v{t.get('version', 1)})"] = t
        
        # Set default index based on selection
        if st.session_state.selected_resource_template and template_id == st.session_state.selected_resource_template.get("id"):
            default_index = list(template_options.keys()).index(f"{template_name} (v{t.get('version', 1)})")
    
    # Template selection dropdown
    options_list = [""] + list(template_options.keys())
    selected_template_label = st.selectbox(
        "Sélectionner un modèle pour les actions:",
        options=options_list,
        index=default_index + 1 if default_index > 0 else 0,
        key=widget_manager.generate_key("template_selector", page_context="resource_template_table"),
        help="Choisissez un modèle dans la liste"
    )
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    is_template_selected = selected_template_label and selected_template_label in template_options
    
    with col1:
        if st.button(
            "📋 Dupliquer", 
            disabled=not is_template_selected,
            use_container_width=True,
            key=widget_manager.generate_key("duplicate_template_btn", page_context="resource_template_table"),
            help="Créer une copie de ce modèle" if is_template_selected else "Sélectionnez d'abord un modèle"
        ):
            selected_template = template_options[selected_template_label]
            st.session_state.duplicating_template = selected_template
            st.rerun()
    
    with col2:
        if st.button(
            "🗑️ Supprimer", 
            disabled=not is_template_selected,
            use_container_width=True,
            key=widget_manager.generate_key("delete_template_btn", page_context="resource_template_table"),
            help="Supprimer définitivement ce modèle" if is_template_selected else "Sélectionnez d'abord un modèle"
        ):
            selected_template = template_options[selected_template_label]
            _delete_resource_template(selected_template, resource_service)
    
    with col3:
        if st.button(
            "✏️ Modifier", 
            disabled=not is_template_selected,
            use_container_width=True,
            key=widget_manager.generate_key("edit_template_btn", page_context="resource_template_table"),
            help="Modifier les propriétés de ce modèle" if is_template_selected else "Sélectionnez d'abord un modèle"
        ):
            selected_template = template_options[selected_template_label]
            st.session_state.editing_resource_template = selected_template
            st.session_state.show_edit_resource_template_form = True
            st.rerun()
    
    # Show selection status
    if is_template_selected:
        selected_template = template_options[selected_template_label]
        st.success(f"**✓ Modèle sélectionné:** {selected_template.get('name')}")
    else:
        st.info("👆 Sélectionnez un modèle pour voir les actions disponibles")
    
    st.markdown('</div>', unsafe_allow_html=True)

def _render_resource_template_form(template: Optional[Dict], all_templates: List[Dict], resource_service, mode: str):
    """Render resource template form for new or edit mode"""
    
    st.markdown("---")
    
    if mode == "edit":
        st.subheader(f"✏️ Modification Modèle: {template.get('name')}")
        form_key = "edit_resource_template_form"
        form_context = "edit_template"
    else:
        st.subheader("➕ Nouveau Modèle de Ressources")
        form_key = "new_resource_template_form"
        form_context = "new_template"
        template = _get_default_resource_template()
    
    with st.form(key=widget_manager.generate_key(form_key, page_context="resource_template_table")):
        st.markdown('<div class="resource-template-form-section">', unsafe_allow_html=True)
        
        # Basic Information Section
        st.markdown("### 📝 Informations de Base")
        col1, col2 = st.columns(2)
        
        with col1:
            template["name"] = st.text_input(
                "Nom du modèle *", 
                value=template.get("name", ""),
                key=widget_manager.generate_key(f"template_name_{form_context}", page_context="resource_template_table")
            )
            template["category"] = st.selectbox(
                "Catégorie *",
                options=["Default", "Commercial", "Residential", "Industrial", "Custom"],
                index=["Default", "Commercial", "Residential", "Industrial", "Custom"].index(template.get("category", "Default")),
                key=widget_manager.generate_key(f"template_category_{form_context}", page_context="resource_template_table")
            )
            
        with col2:
            template["version"] = st.number_input(
                "Version *", 
                value=template.get("version", 1), 
                min_value=1,
                key=widget_manager.generate_key(f"template_version_{form_context}", page_context="resource_template_table")
            )
            template["description"] = st.text_area(
                "Description",
                value=template.get("description", ""),
                key=widget_manager.generate_key(f"template_description_{form_context}", page_context="resource_template_table")
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Settings Section
        st.markdown('<div class="resource-template-form-section">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Paramètres du Modèle")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            template["is_default"] = st.checkbox(
                "Modèle par défaut",
                value=template.get("is_default", False),
                key=widget_manager.generate_key(f"template_default_{form_context}", page_context="resource_template_table")
            )
        
        with col2:
            template["is_shared"] = st.checkbox(
                "Modèle partagé",
                value=template.get("is_shared", False),
                key=widget_manager.generate_key(f"template_shared_{form_context}", page_context="resource_template_table")
            )
        
        with col3:
            template["is_active"] = st.checkbox(
                "Modèle actif",
                value=template.get("is_active", True),
                key=widget_manager.generate_key(f"template_active_{form_context}", page_context="resource_template_table")
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Form actions
        col_save, col_cancel = st.columns(2)
        with col_save:
            submit_label = "💾 Sauvegarder" if mode == "edit" else "➕ Créer Modèle"
            if st.form_submit_button(
                submit_label, 
                use_container_width=True,
                key=widget_manager.generate_key(f"submit_{form_context}", page_context="resource_template_table")
            ):
                if _validate_resource_template(template, all_templates, mode):
                    user_id = 1  # From session
                    if mode == "edit":
                        success = resource_service.update_resource_template(template["name"], template)
                    else:
                        template["user_id"] = user_id
                        success = resource_service.create_resource_template(template)
                    
                    if success:
                        st.success("✅ Modèle sauvegardé avec succès!")
                        _reset_resource_template_form_state()
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la sauvegarde")
        
        with col_cancel:
            if st.form_submit_button(
                "❌ Annuler", 
                use_container_width=True,
                key=widget_manager.generate_key(f"cancel_{form_context}", page_context="resource_template_table")
            ):
                _reset_resource_template_form_state()
                st.rerun()

def _render_duplicate_template_form(original_template: Dict, all_templates: List[Dict], resource_service):
    """Render duplicate template form with name input"""
    
    st.markdown("---")
    st.subheader("📋 Dupliquer le Modèle")
    
    with st.form(key=widget_manager.generate_key("duplicate_template_form", page_context="resource_template_table")):
        st.markdown('<div class="resource-template-form-section">', unsafe_allow_html=True)
        
        new_name = st.text_input(
            "Nouveau nom du modèle *",
            value=f"{original_template.get('name', '')} (Copie)",
            key=widget_manager.generate_key("duplicate_template_name", page_context="resource_template_table")
        )
        
        new_description = st.text_area(
            "Nouvelle description",
            value=original_template.get('description', ''),
            key=widget_manager.generate_key("duplicate_template_description", page_context="resource_template_table")
        )
        
        increment_version = st.checkbox(
            "Incrémenter la version",
            value=True,
            key=widget_manager.generate_key("duplicate_increment_version", page_context="resource_template_table")
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.form_submit_button("✅ Confirmer la duplication", use_container_width=True):
                if new_name:
                    duplicate_data = original_template.copy()
                    duplicate_data['name'] = new_name
                    duplicate_data['description'] = new_description
                    
                    if increment_version:
                        duplicate_data['version'] = duplicate_data.get('version', 1) + 1
                    
                    user_id = 1  # From session
                    duplicate_data['user_id'] = user_id
                    
                    if resource_service.create_resource_template(duplicate_data):
                        st.success(f"✅ Modèle dupliqué: {new_name}")
                        _reset_resource_template_form_state()
                        st.rerun()
                else:
                    st.error("❌ Le nom du modèle est obligatoire")
        
        with col_cancel:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                _reset_resource_template_form_state()
                st.rerun()

def _reset_resource_template_form_state():
    """Reset resource template form state"""
    st.session_state.show_edit_resource_template_form = False
    st.session_state.show_new_resource_template_form = False
    st.session_state.editing_resource_template = None
    st.session_state.duplicating_template = None

def _validate_resource_template(template: Dict, all_templates: List[Dict], mode: str) -> bool:
    """Validate resource template data"""
    errors = []
    
    # Required fields validation
    if not template.get("name", "").strip():
        errors.append("Le nom du modèle est obligatoire")
    
    # Unique name validation for new templates
    if mode == "new":
        existing_names = [t.get("name", "").lower().strip() for t in all_templates]
        if template.get("name", "").lower().strip() in existing_names:
            errors.append("Un modèle avec ce nom existe déjà")
    
    if errors:
        for error in errors:
            st.error(f"❌ {error}")
        return False
    
    return True

def _delete_resource_template(template_to_delete: Dict, resource_service):
    """Delete a resource template"""
    template_name = template_to_delete.get("name")
    
    if resource_service.delete_resource_template(template_name):
        st.success(f"✅ Modèle supprimé: {template_name}")
        st.session_state.selected_resource_template = None
        st.rerun()


def render_filtered_resource_table(filtered_data: Dict, resource_service):
    """Render resource table with current filters and selection - RENAMED to avoid conflict"""
    
    workers = filtered_data.get('workers', [])
    equipment = filtered_data.get('equipment', [])
    
    if not workers and not equipment:
        st.info("Aucune ressource ne correspond aux filtres sélectionnés.")
        return
    
    # Display resource counts
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👷 Ouvriers", len(workers))
    with col2:
        st.metric("🛠️ Équipements", len(equipment))
    
    # Workers Table
    if workers:
        st.subheader("👷 Liste des Ouvriers")
        workers_df = _create_workers_dataframe(workers)
        st.dataframe(workers_df, use_container_width=True, hide_index=True)
        
        # Worker selection
        worker_options = {f"{w['name']} ({w['code']})": w for w in workers}
        selected_worker = st.selectbox(
            "Sélectionner un ouvrier:",
            options=[''] + list(worker_options.keys()),
            key="worker_row_selector"
        )
        
        if selected_worker and selected_worker in worker_options:
            st.session_state.selected_resource_row = worker_options[selected_worker]
            st.success(f"✅ Ouvrier sélectionné: {selected_worker}")
    
    # Equipment Table  
    if equipment:
        st.subheader("🛠️ Liste des Équipements")
        equipment_df = _create_equipment_dataframe(equipment)
        st.dataframe(equipment_df, use_container_width=True, hide_index=True)
        
        # Equipment selection
        equipment_options = {f"{e['name']} ({e['code']})": e for e in equipment}
        selected_equipment = st.selectbox(
            "Sélectionner un équipement:",
            options=[''] + list(equipment_options.keys()),
            key="equipment_row_selector"
        )
        
        if selected_equipment and selected_equipment in equipment_options:
            st.session_state.selected_resource_row = equipment_options[selected_equipment]
            st.success(f"✅ Équipement sélectionné: {selected_equipment}")

def _create_workers_dataframe(workers: List[Dict]) -> pd.DataFrame:
    """Create workers dataframe for display"""
    if not workers:
        return pd.DataFrame()
    
    data = []
    for worker in workers:
        data.append({
            'Nom': worker.get('name', ''),
            'Code': worker.get('code', ''),
            'Spécialité': worker.get('specialty', ''),
            'Catégorie': worker.get('category', ''),
            'Effectif': worker.get('base_count', 0),
            'Taux Horaire': f"€{worker.get('hourly_rate', 0):.2f}",
            'Taux Journalier': f"€{worker.get('daily_rate', 0):.2f}",
            'Max/Équipe': worker.get('max_workers_per_crew', 0),
            'Actif': '✅' if worker.get('is_active', True) else '❌'
        })
    
    return pd.DataFrame(data)

def _create_equipment_dataframe(equipment: List[Dict]) -> pd.DataFrame:
    """Create equipment dataframe for display"""
    if not equipment:
        return pd.DataFrame()
    
    data = []
    for equip in equipment:
        data.append({
            'Nom': equip.get('name', ''),
            'Code': equip.get('code', ''),
            'Type': equip.get('type', ''),
            'Catégorie': equip.get('category', ''),
            'Modèle': equip.get('model', ''),
            'Quantité': equip.get('base_count', 0),
            'Taux Horaire': f"€{equip.get('hourly_rate', 0):.2f}",
            'Taux Journalier': f"€{equip.get('daily_rate', 0):.2f}",
            'Capacité': equip.get('capacity', ''),
            'Opérateur': '✅' if equip.get('requires_operator', False) else '❌',
            'Disponible': '✅' if equip.get('is_available', True) else '❌'
        })
    
    return pd.DataFrame(data)