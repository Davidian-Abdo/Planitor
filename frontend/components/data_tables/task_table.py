"""
OPTIMIZED Task Table Component - Civil Engineering Scheduling
Professional, simplified, and maintainable with widget manager
"""
import streamlit as st
import pandas as pd
import json
from typing import List, Dict, Optional, Any
import logging
from backend.utils.widget_manager import widget_manager

from frontend.helpers.template_context import template_context

logger = logging.getLogger(__name__)

# French column mapping
FRENCH_COLUMNS = {
    "base_task_id": "ID Tâche", "name": "Nom", "discipline": "Discipline", 
    "sub_discipline": "Sous-Discipline", "resource_type": "Type Ressource",
    "task_type": "Type", "base_duration": "Durée Base", 
    "unit_duration": "Durée Unitaire", "duration_calculation_method": "Méthode Calcul",
    "min_crews_needed": "Équipes Min", "max_crews_allowed": "Équipes Max",
    "min_equipment_needed": "Équipements Min", "max_equipment_allowed": "Équipements Max",
    "predecessors": "Prédécesseurs", "repeat_on_floor": "Répétition Étage",
    "delay": "Délai", "weather_sensitive": "Sensible Météo", 
    "quality_gate": "Point Contrôle", "included": "Incluse"
}

# Duration calculation methods
DURATION_METHODS = {
    "fixed_duration": "Durée Fixe",
    "quantity_based": "Basé sur la Quantité", 
    "resource_calculation": "Calcul par Ressources"
}


def render_tasks_table(tasks: List[Dict], task_service, user_id: int, available_resources: Dict[str, List[Dict]] = None, template_service=None):
    """Main task table with essential context integration"""
    # Show context status
    if template_context.is_ready():
        resource = template_context.resource_template
        task = template_context.task_template
        st.success(f"🎯 Contexte: {resource['name']} + {task.get('name', 'Sans nom')}")
    
    # Initialize state
    if 'task_form_state' not in st.session_state:
        st.session_state.task_form_state = {'mode': None, 'current_task': None}
    
    state = st.session_state.task_form_state
    
    # Apply filters
    filtered_tasks = _render_task_filters(tasks)
    
    # Show statistics
    _render_statistics(tasks, filtered_tasks)
    
    # Handle form mode
    if state['mode']:
        _render_task_form(state, tasks, task_service, user_id, available_resources, template_service)
        return
    
    # Main table interface
    _render_table_interface(filtered_tasks, task_service, user_id)

def _render_statistics(all_tasks: List[Dict], filtered_tasks: List[Dict]):
    """Essential statistics"""
    total_count = len(all_tasks)
    filtered_count = len(filtered_tasks)
    included_count = len([t for t in filtered_tasks if t.get('included', True)])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📋 Tâches", f"{filtered_count}/{total_count}")
    col2.metric("✅ Incluses", included_count)
    col3.metric("🎯 Contexte", "✅" if template_context.is_ready() else "⚠️")

def _render_task_filters(tasks: List[Dict]) -> List[Dict]:
    """Essential filters"""
    if not tasks:
        return []
    
    disciplines = sorted(set(t.get('discipline', '') for t in tasks if t.get('discipline')))
    
    col1, col2 = st.columns(2)
    with col1:
        selected_discipline = st.selectbox(
            "Discipline",
            options=['Toutes'] + disciplines,
            key=widget_manager.generate_key("filter_discipline", "task_table")
        )
    with col2:
        included_only = st.checkbox("Afficher seulement les incluses", value=True,
                                  key=widget_manager.generate_key("filter_included", "task_table"))
    
    # Apply filters
    filtered = tasks
    if selected_discipline != 'Toutes':
        filtered = [t for t in filtered if t.get('discipline') == selected_discipline]
    if included_only:
        filtered = [t for t in filtered if t.get('included', True)]
    
    return filtered

def _render_table_interface(tasks: List[Dict], task_service, user_id: int):
    """Main table interface"""
    selected_task = _render_task_selection(tasks)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Nouvelle Tâche", use_container_width=True):
            st.session_state.task_form_state = {'mode': 'new', 'current_task': None}
            st.rerun()
    
    with col2:
        disabled = selected_task is None
        if st.button("✏️ Modifier", use_container_width=True, disabled=disabled):
            st.session_state.task_form_state = {'mode': 'edit', 'current_task': selected_task}
            st.rerun()
    
    with col3:
        if st.button("📋 Dupliquer", use_container_width=True, disabled=disabled):
            st.session_state.task_form_state = {'mode': 'duplicate', 'current_task': selected_task}
            st.rerun()
    
    with col4:
        if st.button("🗑️ Supprimer", use_container_width=True, disabled=disabled):
            _delete_task(selected_task, tasks, task_service, user_id)
            st.rerun()
    
    # Context actions
    if template_context.is_ready() and selected_task:
        st.markdown("---")
        if st.button("🔗 Tester Compatibilité", use_container_width=True):
            _test_compatibility(selected_task, template_service)
    
    # Data table
    _render_data_table(tasks)

def _test_compatibility(task: Dict, template_service=None):
    """Test task compatibility with current context"""
    try:
        if template_service is None:
            st.error("❌ Service de template non disponible")
            return
        
        validation = template_service.validate_template_compatibility(
            template_context.resource_template,
            task
        )
        
        if validation['compatible']:
            st.success("✅ Tâche compatible avec le contexte!")
        else:
            st.error("❌ Problèmes de compatibilité")
            
        # Show issues
        if validation['issues']:
            st.write("**Problèmes:**")
            for issue in validation['issues']:
                st.write(f"- {issue}")
                
    except Exception as e:
        st.error(f"❌ Erreur: {e}")

def _render_task_selection(tasks: List[Dict]) -> Optional[Dict]:
    """Task selection dropdown"""
    if not tasks:
        st.info("📭 Aucune tâche disponible")
        return None
        
    options = {f"{t.get('name', 'Sans nom')} ({t.get('base_task_id', 'N/A')})": t for t in tasks}
    
    selected = st.selectbox(
        "Sélectionner une tâche:",
        options=[''] + list(options.keys()),
        key=widget_manager.generate_key("task_selector", "task_table")
    )
    
    if selected and selected in options:
        return options[selected]
    
    return None

def _render_data_table(tasks: List[Dict]):
    """Data table display"""
    if not tasks:
        st.info("📭 Aucune tâche à afficher")
        return
    
    df = _tasks_to_dataframe(tasks)
    
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Incluse": st.column_config.CheckboxColumn("Incluse"),
            "Durée Base": st.column_config.NumberColumn("Durée (jours)", min_value=1),
            "Équipes Min": st.column_config.NumberColumn("Équipes Min", min_value=1)
        },
        key=widget_manager.generate_key("task_data_editor", "task_table")
    )
    
    if st.button("💾 Sauvegarder Modifications", use_container_width=True):
        _save_table_changes(edited_df, tasks)
        st.success("✅ Modifications sauvegardées!")
        st.rerun()

def _tasks_to_dataframe(tasks: List[Dict]) -> pd.DataFrame:
    """Convert tasks to DataFrame"""
    if not tasks:
        return pd.DataFrame()
    
    display_data = []
    for task in tasks:
        row = {}
        for eng_col, fr_col in FRENCH_COLUMNS.items():
            if eng_col in task:
                value = task[eng_col]
                if eng_col == 'min_equipment_needed':
                    equipment = task.get('min_equipment_needed', {})
                    row[fr_col] = ", ".join([f"{k}({v})" for k, v in equipment.items()]) if equipment else "Aucun"
                elif eng_col == 'predecessors':
                    preds = task.get('predecessors', [])
                    row[fr_col] = ", ".join(preds) if preds else "Aucun"
                elif eng_col in ['repeat_on_floor', 'weather_sensitive', 'quality_gate', 'included']:
                    row[fr_col] = '✅' if value else '❌'
                else:
                    row[fr_col] = value
        
        display_data.append(row)
    
    return pd.DataFrame(display_data)

def _render_task_form(state: Dict, all_tasks: List[Dict], task_service, user_id: int, available_resources: Dict[str, List[Dict]] = None, template_service=None):
    """Unified form for new/edit/duplicate operations"""
    mode = state['mode']
    task = state['current_task']
    
    st.markdown("---")
    
    if mode == 'edit':
        title = f"✏️ Modification: {task.get('name')}"
        submit_label = "💾 Sauvegarder"
    elif mode == 'duplicate':
        title = "📋 Duplication de Tâche"
        submit_label = "✅ Créer Copie"
        task = task.copy() if task else None
    else:  # new
        title = "➕ Nouvelle Tâche"
        submit_label = "➕ Créer Tâche"
        task = _get_default_task_template()
    
    st.subheader(title)
    
    with st.form(key=widget_manager.generate_key("task_form", "task_table")):
        # Basic Information
        task = _render_basic_info_section(task, mode)
        
        # Duration Calculation
        task = _render_duration_section(task)
        
        # Resource Selection (Workers & Equipment)
        task = _render_resource_selection_section(task, available_resources)
        
        # Predecessors
        task = _render_predecessors_section(task, all_tasks)
        
        # Options
        task = _render_options_section(task)
        
        # Form Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button(submit_label, use_container_width=True,
                                   key=widget_manager.generate_key("form_submit", "task_table")):
                if _validate_task(task, all_tasks, mode):
                    _save_task(task, all_tasks, task_service, user_id, mode)
        
        with col2:
            if st.form_submit_button("❌ Annuler", use_container_width=True,
                                   key=widget_manager.generate_key("form_cancel", "task_table")):
                st.session_state.task_form_state = {'mode': None, 'current_task': None}
                st.rerun()

def _render_basic_info_section(task: Dict, mode: str) -> Dict:
    """Essential task information"""
    st.markdown("### 📝 Informations de Base")
    
    col1, col2 = st.columns(2)
    with col1:
        task["name"] = st.text_input(
            "Nom de la tâche *", 
            value=task.get("name", ""),
            key=widget_manager.generate_key("task_name", "task_table")
        )
        task["discipline"] = st.text_input(
            "Discipline *", 
            value=task.get("discipline", ""),
            key=widget_manager.generate_key("task_discipline", "task_table")
        )
        
    with col2:
        task["sub_discipline"] = st.text_input(
            "Sous-discipline *", 
            value=task.get("sub_discipline", ""),
            key=widget_manager.generate_key("task_sub_discipline", "task_table")
        )
        task["resource_type"] = st.text_input(
            "Type de ressource", 
            value=task.get("resource_type", ""),
            key=widget_manager.generate_key("task_resource_type", "task_table")
        )
    
    task["task_type"] = st.selectbox(
        "Type de tâche *",
        options=["worker", "equipment", "parallel", "hybrid"],
        index=["worker", "equipment", "parallel", "hybrid"].index(task.get("task_type", "execution")),
        key=widget_manager.generate_key("task_task_type", "task_table")
    )
    
    return task

def _render_duration_section(task: Dict) -> Dict:
    """Duration calculation with business logic"""
    st.markdown("### ⏱️ Calcul de la Durée")
    
    # Method selection
    current_method = task.get("duration_calculation_method", "fixed_duration")
    method_display = DURATION_METHODS.get(current_method, current_method)
    
    selected_display = st.selectbox(
        "Méthode de calcul *",
        options=list(DURATION_METHODS.values()),
        index=list(DURATION_METHODS.values()).index(method_display),
        key=widget_manager.generate_key("duration_method", "task_table")
    )
    
    # Get method key from display name
    method = next(k for k, v in DURATION_METHODS.items() if v == selected_display)
    task["duration_calculation_method"] = method
    
    # Dynamic fields based on method
    col1, col2 = st.columns(2)
    with col1:
        if method == "fixed_duration":
            task["base_duration"] = st.number_input(
                "Durée fixe (jours) *", 
                value=task.get("base_duration", 1), 
                min_value=1,
                key=widget_manager.generate_key("base_duration", "task_table")
            )
            task["unit_duration"] = 0
        elif method == "quantity_based":
            task["unit_duration"] = st.number_input(
                "Durée par unité (jours) *", 
                value=task.get("unit_duration", 1), 
                min_value=1,
                key=widget_manager.generate_key("unit_duration", "task_table")
            )
            task["base_duration"] = 0
        else:  # resource_calculation
            task["base_duration"] = 0
            task["unit_duration"] = 0
            st.info("✅ Durée calculée automatiquement selon les ressources disponibles")
    
    with col2:
        task["min_crews_needed"] = st.number_input(
            "Équipes minimum *", 
            value=task.get("min_crews_needed", 1), 
            min_value=1,
            key=widget_manager.generate_key("min_crews", "task_table")
        )
        
        task["max_crews_allowed"] = st.number_input(
            "Équipes maximum", 
            value=task.get("max_crews_allowed", task.get("min_crews_needed", 1)), 
            min_value=task.get("min_crews_needed", 1),
            key=widget_manager.generate_key("max_crews", "task_table")
        )
    
    return task

def _render_resource_selection_section(task: Dict, available_resources: Dict[str, List[Dict]] = None) -> Dict:
    """Resource selection section - workers and equipment from resource templates"""
    st.markdown("### 👥🛠️ Sélection des Ressources")
    
    # Initialize available resources if not provided
    if available_resources is None:
        available_resources = {'workers': [], 'equipment': []}
    
    workers = available_resources.get('workers', [])
    equipment = available_resources.get('equipment', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👥 Ouvriers Requis")
        
        if not workers:
            st.warning("⚠️ Aucun ouvrier disponible. Configurez d'abord les ouvriers dans le modèle de ressources.")
        else:
            # Worker type selection
            worker_options = {f"{w.get('name', '')} ({w.get('specialty', '')})": w for w in workers}
            current_worker_type = task.get('resource_type', '')
            
            # Find matching worker
            selected_worker_key = None
            for key, worker_data in worker_options.items():
                if worker_data.get('name') == current_worker_type or worker_data.get('specialty') == current_worker_type:
                    selected_worker_key = key
                    break
            
            selected_worker = st.selectbox(
                "Type d'ouvrier requis",
                options=[''] + list(worker_options.keys()),
                index=list(worker_options.keys()).index(selected_worker_key) + 1 if selected_worker_key else 0,
                key=widget_manager.generate_key("worker_type_select", "task_table")
            )
            
            if selected_worker and selected_worker in worker_options:
                worker_data = worker_options[selected_worker]
                task["resource_type"] = worker_data.get('specialty', worker_data.get('name'))
    
    with col2:
        st.markdown("#### 🛠️ Équipements Requis")
        
        current_equipment = task.get("min_equipment_needed", {})
        
        if not equipment:
            st.warning("⚠️ Aucun équipement disponible. Configurez d'abord les équipements dans le modèle de ressources.")
        else:
            # Convert available equipment to selection options
            equipment_options = {f"{eq.get('name', '')} ({eq.get('code', '')})": eq for eq in equipment}
            
            # Display current equipment with selection
            if current_equipment:
                st.write("**Équipements configurés:**")
                
                equipment_to_remove = []
                for idx, (equip_name, quantity) in enumerate(current_equipment.items()):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Find matching equipment from available options
                        current_equip_key = None
                        for key, eq_data in equipment_options.items():
                            if eq_data.get('name') == equip_name or eq_data.get('code') == equip_name:
                                current_equip_key = key
                                break
                        
                        selected_equip = st.selectbox(
                            f"Équipement {idx+1}",
                            options=[''] + list(equipment_options.keys()),
                            index=list(equipment_options.keys()).index(current_equip_key) + 1 if current_equip_key else 0,
                            key=widget_manager.generate_key(f"equip_select_{idx}", "task_table")
                        )
                    
                    with col2:
                        if selected_equip:
                            selected_qty = st.number_input(
                                f"Quantité {idx+1}",
                                value=int(quantity),
                                min_value=1,
                                key=widget_manager.generate_key(f"equip_qty_{idx}", "task_table")
                            )
                        else:
                            selected_qty = 0
                    
                    with col3:
                        st.text("")  # Spacer
                        if st.checkbox("🗑️", key=widget_manager.generate_key(f"remove_equip_{idx}", "task_table")):
                            equipment_to_remove.append(equip_name)
                    
                    # Update equipment
                    if selected_equip and selected_equip in equipment_options:
                        equip_data = equipment_options[selected_equip]
                        equip_code = equip_data.get('code', equip_data.get('name'))
                        if equip_code != equip_name:
                            # Remove old name, add new one
                            current_equipment[equip_code] = selected_qty
                            if equip_name in current_equipment:
                                del current_equipment[equip_name]
                        else:
                            current_equipment[equip_name] = selected_qty
                
                # Remove marked equipment
                for equip_name in equipment_to_remove:
                    if equip_name in current_equipment:
                        del current_equipment[equip_name]
                        st.rerun()
            
            # Add new equipment section
            st.markdown("**Ajouter un équipement:**")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                new_equip_select = st.selectbox(
                    "Sélectionner un équipement",
                    options=[''] + list(equipment_options.keys()),
                    key=widget_manager.generate_key("new_equip_select", "task_table")
                )
            with col2:
                new_equip_qty = st.number_input(
                    "Quantité",
                    min_value=1,
                    value=1,
                    key=widget_manager.generate_key("new_equip_qty", "task_table")
                )
            
            # Auto-add when equipment is selected (form-safe approach)
            if new_equip_select and new_equip_select in equipment_options:
                equip_data = equipment_options[new_equip_select]
                equip_code = equip_data.get('code', equip_data.get('name'))
                current_equipment[equip_code] = new_equip_qty
                st.success(f"✅ {equip_data.get('name')} ajouté")
    
    # Resource management instructions
    st.info("""
    💡 **Instructions:**
    - Sélectionnez le type d'ouvrier requis pour cette tâche
    - Pour les équipements: sélectionnez dans la liste et définissez les quantités
    - Cochez 🗑️ pour supprimer un équipement
    - Les ressources doivent être configurées dans le modèle de ressources
    """)
    
    task["min_equipment_needed"] = current_equipment
    return task

def _render_predecessors_section(task: Dict, all_tasks: List[Dict]) -> Dict:
    """Predecessors management - FIXED for form compatibility"""
    st.markdown("#### 🔗 Prédécesseurs")
    
    predecessors = task.get("predecessors", [])
    available_tasks = [t["base_task_id"] for t in all_tasks 
                      if t.get("base_task_id") != task.get("base_task_id")]
    
    # Use multi-select instead of dynamic buttons
    selected_predecessors = st.multiselect(
        "Sélectionnez les prédécesseurs:",
        options=available_tasks,
        default=predecessors,
        key=widget_manager.generate_key("predecessors_multiselect", "task_table"),
        help="Maintenez Ctrl (Cmd sur Mac) pour sélectionner plusieurs tâches"
    )
    
    # Show current selection
    if selected_predecessors:
        st.write("**Prédécesseurs sélectionnés:**")
        for pred in selected_predecessors:
            st.write(f"• {pred}")
    else:
        st.info("Aucun prédécesseur sélectionné")
    
    task["predecessors"] = selected_predecessors
    return task

def _render_options_section(task: Dict) -> Dict:
    """Task options - SIMPLIFIED layout"""
    st.markdown("### ⚙️ Options de Tâche")
    
    col1, col2 = st.columns(2)
    with col1:
        task["repeat_on_floor"] = st.checkbox(
            "Répéter par étage",
            value=task.get("repeat_on_floor", False),
            key=widget_manager.generate_key("repeat_floor", "task_table")
        )
        task["weather_sensitive"] = st.checkbox(
            "Sensible à la météo",
            value=task.get("weather_sensitive", False),
            key=widget_manager.generate_key("weather_sensitive", "task_table")
        )
    
    with col2:
        task["quality_gate"] = st.checkbox(
            "Point de contrôle qualité", 
            value=task.get("quality_gate", False),
            key=widget_manager.generate_key("quality_gate", "task_table")
        )
        task["included"] = st.checkbox(
            "Inclure dans le planning",
            value=task.get("included", True),
            key=widget_manager.generate_key("included", "task_table")
        )
    
    return task


def _save_table_changes(edited_df: pd.DataFrame, tasks: List[Dict]):
    """Save changes from data editor"""
    st.info("Fonctionnalité de sauvegarde en ligne à implémenter")

def _validate_task(task: Dict, all_tasks: List[Dict], mode: str) -> bool:
    """Essential validation"""
    errors = []
    
    if not task.get("name", "").strip():
        errors.append("Le nom de la tâche est obligatoire")
    if not task.get("discipline", "").strip():
        errors.append("La discipline est obligatoire")
    if not task.get("sub_discipline", "").strip():
        errors.append("La sous-discipline est obligatoire")
    
    method = task.get("duration_calculation_method", "fixed_duration")
    if method == "fixed_duration" and task.get("base_duration", 0) <= 0:
        errors.append("La durée fixe doit être positive")
    elif method == "quantity_based" and task.get("unit_duration", 0) <= 0:
        errors.append("La durée unitaire doit être positive")
    
    if task.get("min_crews_needed", 0) <= 0:
        errors.append("Le nombre d'équipes doit être positif")
    
    if mode == "new":
        existing_names = [t.get("name", "").lower() for t in all_tasks]
        if task.get("name", "").lower() in existing_names:
            errors.append("Une tâche avec ce nom existe déjà")
    
    for error in errors:
        st.error(f"❌ {error}")
    
    return len(errors) == 0

def _save_task(task: Dict, tasks: List[Dict], task_service, user_id: int, mode: str):
    """Save task via service layer"""
    try:
        if mode == 'edit':
            # Use the task ID from the original task being edited
            result = task_service.update_custom_task(user_id, task.get('id'), task)
            if result:
                # Update local list
                for i, t in enumerate(tasks):
                    if t.get('id') == task.get('id'):
                        tasks[i] = result
                        break
                st.success("✅ Tâche modifiée avec succès!")
            else:
                st.error("❌ Erreur lors de la modification")
                
        elif mode == 'new':
            # Create new task - service will generate ID
            result = task_service.create_custom_task(user_id, task)
            if result:
                tasks.append(result)
                st.success(f"✅ Tâche créée: {result.get('base_task_id')}")
            else:
                st.error("❌ Erreur lors de la création")
            
        elif mode == 'duplicate':
            # Create duplicate - service will generate new ID
            duplicate_task = task.copy()
            duplicate_task['base_task_id'] = None  # Let service generate new ID
            result = task_service.create_custom_task(user_id, duplicate_task)
            if result:
                tasks.append(result)
                st.success(f"✅ Tâche dupliquée: {result.get('base_task_id')}")
            else:
                st.error("❌ Erreur lors de la duplication")
        
        # Clear form state
        st.session_state.task_form_state = {'mode': None, 'current_task': None}
        
    except Exception as e:
        logger.error(f"Error saving task: {e}")
        st.error(f"❌ Erreur: {e}")

def _delete_task(task: Dict, tasks: List[Dict], task_service, user_id: int):
    """Delete task with confirmation"""
    task_id = task.get('base_task_id')
    task_name = task.get('name')
    
    st.warning(f"Êtes-vous sûr de vouloir supprimer '{task_name}'?")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirmer", key=widget_manager.generate_key("confirm_delete", "task_table")):
            try:
                # Call service to delete
                success = task_service.delete_custom_task(user_id, task.get('id'))
                if success:
                    # Remove from local list
                    tasks[:] = [t for t in tasks if t.get('base_task_id') != task_id]
                    st.success(f"✅ Tâche supprimée: {task_id}")
                else:
                    st.error("❌ Erreur lors de la suppression")
            except Exception as e:
                logger.error(f"Error deleting task: {e}")
                st.error(f"❌ Erreur: {e}")
    
    with col2:
        if st.button("❌ Annuler", key=widget_manager.generate_key("cancel_delete", "task_table")):
            st.info("Suppression annulée")

def _get_default_task_template() -> Dict:
    """Default task template"""
    return {
        "base_task_id": "", "name": "", "discipline": "", "sub_discipline": "",
        "resource_type": "", "task_type": "hybrid", "base_duration": 1,
        "unit_duration": 0, "duration_calculation_method": "fixed_duration",
        "min_crews_needed": 1, "max_crews_allowed": 1, "delay": 0,
        "min_equipment_needed": {}, "max_equipment_allowed": {},
        "predecessors": [], "repeat_on_floor": False, "weather_sensitive": False,
        "quality_gate": False, "included": True
    }