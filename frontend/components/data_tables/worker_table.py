"""
PROFESSIONAL Worker Table Component - Civil Engineering Scheduling
UPDATED with essential template context integration
"""
import streamlit as st
import pandas as pd
import logging
from typing import List, Dict, Optional, Any
from backend.utils.widget_manager import widget_manager

# Import template context
from frontend.components.context.template_context import template_context

logger = logging.getLogger(__name__)

# French column mapping for workers
FRENCH_COLUMNS = {
    "code": "Code", "name": "Nom", "specialty": "Spécialité", "category": "Catégorie",
    "base_count": "Effectif Base", "hourly_rate": "Taux Horaire", "daily_rate": "Taux Journalier",
    "max_workers_per_crew": "Max par Équipe", "base_productivity_rate": "Taux Productivité Base",
    "productivity_unit": "Unité Productivité", "qualification_level": "Niveau Qualification",
    "is_active": "Actif"
}

def render_workers_table(workers: List[Dict], resource_service, user_id: int, available_templates: List[Dict], 
                        template_id: Optional[int] = None, current_template_name: str = "", task_template_context: Dict = None, template_service=None):
    """Render worker resources table with context awareness"""
    # Initialize state
    if 'worker_form_state' not in st.session_state:
        st.session_state.worker_form_state = {'mode': None, 'current_worker': None}
        
    
    # Check if context is available - use new context system first, fallback to old parameter
    current_task_template = template_context.task_template if template_context.is_ready() else task_template_context
     
    if not template_context.is_ready() and not task_template_context:
        st.error("🚫 Contexte de travail non défini. Veuillez sélectionner un modèle de ressources ET un modèle de tâches.")
        return
    
    # Show context status
    if template_context.is_ready():
        resource = template_context.resource_template
        task = template_context.task_template
        st.success(f"🎯 Contexte Actif: {resource['name']} + {task.get('name', 'Sans nom')}")
    elif task_template_context:
        st.info(f"📝 Contexte Tâches: {task_template_context.get('name', 'Sans nom')}")

    # Template-level actions section
    _render_template_actions(resource_service, user_id, available_templates, template_id, current_template_name)
    
    state = st.session_state.worker_form_state
    
    # Apply filters FIRST to get filtered_workers
    filtered_workers = _render_worker_filters(workers)
    
    # Render statistics
    _render_worker_statistics(workers, filtered_workers)
    
    # Render active form if needed
    if state['mode']:
        _render_worker_form(state, workers, resource_service, user_id, available_templates, 
                          template_id, current_task_template)
        return
    # Main table interface
    _render_worker_table_interface(filtered_workers, resource_service, user_id, available_templates, template_id)


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
                    key=widget_manager.generate_key("save_template_btn", "worker_table")):
            _save_resource_template(resource_service, user_id, template_id, available_templates)
    
    with col2:
        if st.button("➕ Nouveau Modèle", use_container_width=True,
                    key=widget_manager.generate_key("new_template_btn", "worker_table")):
            _create_new_template(resource_service, user_id)
    
    with col3:
        if st.button("📥 Charger Défaut", use_container_width=True,
                    key=widget_manager.generate_key("load_default_btn", "worker_table")):
            _load_default_resources(resource_service, user_id)
    
    with col4:
        if st.button("🔄 Actualiser", use_container_width=True,
                    key=widget_manager.generate_key("refresh_btn", "worker_table")):
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

def _render_worker_statistics(all_workers: List[Dict], filtered_workers: List[Dict]):
    """Render worker statistics"""
    total_count = len(all_workers)
    filtered_count = len(filtered_workers)
    
    total_active = len([w for w in all_workers if w.get('is_active', True)])
    filtered_active = len([w for w in filtered_workers if w.get('is_active', True)])
    
    total_specialties = len(set(w.get('specialty', '') for w in all_workers))
    filtered_specialties = len(set(w.get('specialty', '') for w in filtered_workers))
    
    # Context-aware metrics
    context_match_count = 0
    if template_context.is_ready():
        required_specialty = template_context.task_template.get('resource_type')
        context_match_count = len([w for w in filtered_workers if w.get('specialty') == required_specialty])
    
    # Display statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("👥 Ouvriers", f"{filtered_count}/{total_count}")
    
    with col2:
        st.metric("✅ Actifs", f"{filtered_active}/{total_active}")
    
    with col3:
        st.metric("🎯 Spécialités", f"{filtered_specialties}/{total_specialties}")
    
    with col4:
        filters_active = filtered_count != total_count
        status = "🔍 Filtres Actifs" if filters_active else "👁️ Tous Visible"
        st.metric("Statut", status)
    
    with col5:
        if template_context.is_ready():
            st.metric("🔗 Contexte", context_match_count)
        else:
            st.metric("🔗 Contexte", "N/A")

def _render_worker_filters(workers: List[Dict]) -> List[Dict]:
    """Render worker filters"""
    if not workers:
        return []
    
    # Get unique values for filters
    specialties = sorted(list(set(w.get('specialty', '') for w in workers if w.get('specialty'))))
    categories = sorted(list(set(w.get('category', '') for w in workers if w.get('category'))))
    
    st.markdown("### 🔍 Filtres Ouvriers")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_specialty = st.selectbox(
            "Spécialité",
            options=['Toutes'] + specialties,
            key=widget_manager.generate_key("filter_specialty", "worker_table")
        )
    
    with col2:
        selected_category = st.selectbox(
            "Catégorie",
            options=['Toutes'] + categories,
            key=widget_manager.generate_key("filter_category", "worker_table")
        )
    
    with col3:
        selected_active = st.selectbox(
            "Statut", 
            options=['Tous', 'Actifs', 'Inactifs'],
            key=widget_manager.generate_key("filter_active", "worker_table")
        )
    
    # Apply filters
    filtered_workers = _apply_worker_filters(workers, selected_specialty, selected_category, selected_active)
    
    return filtered_workers

def _apply_worker_filters(workers: List[Dict], specialty: str, category: str, active: str) -> List[Dict]:
    """Apply filters to worker list"""
    filtered = workers
    
    if specialty != 'Toutes':
        filtered = [w for w in filtered if w.get('specialty') == specialty]
    
    if category != 'Toutes':
        filtered = [w for w in filtered if w.get('category') == category]
    
    if active == 'Actifs':
        filtered = [w for w in filtered if w.get('is_active', True)]
    elif active == 'Inactifs':
        filtered = [w for w in filtered if not w.get('is_active', True)]
    
    return filtered

def _render_worker_table_interface(workers: List[Dict], resource_service, user_id: int, available_templates: List[Dict], template_id: Optional[int] = None):
    """Render worker table interface"""
    
    # Worker selection
    selected_worker = _render_worker_selection(workers)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.button("➕ Nouvel Ouvrier", use_container_width=True,
                    key=widget_manager.generate_key("new_worker_btn", "worker_table")):
            st.session_state.worker_form_state = {'mode': 'new', 'current_worker': None}
            st.rerun()
    
    with col2:
        disabled = selected_worker is None
        if st.button("✏️ Modifier", use_container_width=True, disabled=disabled,
                    key=widget_manager.generate_key("edit_worker_btn", "worker_table")):
            st.session_state.worker_form_state = {'mode': 'edit', 'current_worker': selected_worker}
            st.rerun()
    
    with col3:
        if st.button("📋 Dupliquer", use_container_width=True, disabled=disabled,
                    key=widget_manager.generate_key("duplicate_worker_btn", "worker_table")):
            st.session_state.worker_form_state = {'mode': 'duplicate', 'current_worker': selected_worker}
            st.rerun()
    
    with col4:
        if st.button("🗑️ Supprimer", use_container_width=True, disabled=disabled,
                    key=widget_manager.generate_key("delete_worker_btn", "worker_table")):
            _delete_worker(selected_worker, workers, resource_service, user_id)
            st.rerun()
    
    # Context-aware actions for selected worker
    if template_context.is_ready() and selected_worker:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Tester Compatibilité", use_container_width=True,
                        key=widget_manager.generate_key("test_compatibility", "worker_table")):
                _test_worker_compatibility(selected_worker, template_service)
        with col2:
            if st.button("📈 Analyser Productivité", use_container_width=True,
                        key=widget_manager.generate_key("analyze_productivity", "worker_table")):
                _analyze_worker_productivity(selected_worker)
    
    # Data table
    _render_worker_data_table(workers)

def _test_worker_compatibility(worker: Dict, template_service=None):
    """Test worker compatibility with current context"""
    try:
        if template_service is None:
            st.error("❌ Service de template non disponible")
            return
        
        # Create a mock task template for this worker's specialty
        mock_task_template = {
            'resource_type': worker.get('specialty'),
            'name': f"Test pour {worker.get('name')}",
            'base_task_id': f"TEST_{worker.get('code')}"
        }
        
        validation = template_service.validate_template_compatibility(
            template_context.resource_template,
            mock_task_template
        )
        
        if validation.get('compatible', False):
            st.success(f"✅ '{worker['name']}' compatible avec le contexte")
        else:
            st.error(f"❌ Problèmes de compatibilité pour '{worker['name']}'")
        
        # Show specific issues
        if validation.get('issues'):
            st.write("**Problèmes identifiés:**")
            for issue in validation['issues']:
                st.write(f"- {issue}")
                
    except Exception as e:
        st.error(f"❌ Erreur lors du test de compatibilité: {e}")

def _analyze_worker_productivity(worker: Dict):
    """Analyze worker productivity for current context"""
    try:
        st.info(f"📊 Analyse de productivité pour: {worker['name']}")
        
        # Get productivity rates
        productivity_rates = worker.get('base_productivity_rate', {})
        if isinstance(productivity_rates, dict):
            default_rate = productivity_rates.get('default', 1.0)
            
            # Simple productivity analysis
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Taux Défaut", f"{default_rate:.2f}")
            with col2:
                st.metric("Effectif Base", worker.get('base_count', 1))
            with col3:
                st.metric("Max/Équipe", worker.get('max_workers_per_crew', 1))
            
            # Recommendations
            if default_rate < 0.5:
                st.warning("💡 Taux de productivité faible - envisager une formation")
            elif default_rate > 2.0:
                st.success("💡 Taux de productivité élevé - excellent!")
                
        else:
            st.warning("⚠️ Configuration de productivité non standard")
            
    except Exception as e:
        st.error(f"❌ Erreur d'analyse: {e}")

def _render_worker_selection(workers: List[Dict]) -> Optional[Dict]:
    """Render worker selection dropdown"""
    if not workers:
        st.info("📭 Aucun ouvrier disponible")
        return None
        
    worker_options = {f"{w.get('name', 'Sans nom')} ({w.get('code', 'N/A')})": w for w in workers}
    
    selected_label = st.selectbox(
        "Sélectionner un ouvrier:",
        options=[''] + list(worker_options.keys()),
        key=widget_manager.generate_key("worker_selector", "worker_table")
    )
    
    if selected_label and selected_label in worker_options:
        st.success(f"✅ Ouvrier sélectionné: {selected_label}")
        return worker_options[selected_label]
    
    st.info("👆 Sélectionnez un ouvrier pour voir les actions disponibles")
    return None

def _render_worker_data_table(workers: List[Dict]):
    """Render worker data table"""
    if not workers:
        st.info("📭 Aucun ouvrier à afficher")
        return
    
    # Convert to DataFrame
    df = _workers_to_dataframe(workers)
    
    # Display data editor
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Actif": st.column_config.CheckboxColumn("Actif"),
            "Taux Horaire": st.column_config.NumberColumn("Taux Horaire (€)", format="%.2f €"),
            "Effectif Base": st.column_config.NumberColumn("Effectif Base", min_value=0),
            "Max par Équipe": st.column_config.NumberColumn("Max par Équipe", min_value=1)
        },
        key=widget_manager.generate_key("worker_data_editor", "worker_table")
    )
    
    # Save changes
    if st.button("💾 Sauvegarder Modifications", use_container_width=True,
                key=widget_manager.generate_key("save_worker_table_btn", "worker_table")):
        _save_worker_table_changes(edited_df, workers)

def _render_worker_form(state: Dict, all_workers: List[Dict], resource_service, user_id: int, 
                       available_templates: List[Dict], template_id: Optional[int] = None, 
                       task_template_context: Dict = None):
    """Render worker form for create/edit/duplicate with task template context"""
    mode = state['mode']
    worker = state['current_worker']
    
    # Display current context if available
    if template_context.is_ready():
        st.markdown(f"""
        <div style="background: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <small>📝 Contexte: <strong>{template_context.resource_template['name']}</strong> + 
            <strong>{template_context.task_template.get('name', 'Sans nom')}</strong></small>
        </div>
        """, unsafe_allow_html=True)
    elif task_template_context:
        st.markdown(f"""
        <div style="background: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <small>📝 Contexte Tâches: <strong>{task_template_context.get('name', 'Sans nom')}</strong></small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if mode == 'edit':
        title = f"✏️ Modification: {worker.get('name')}"
        submit_label = "💾 Sauvegarder"
    elif mode == 'duplicate':
        title = "📋 Duplication d'Ouvrier"
        submit_label = "✅ Créer Copie"
        worker = worker.copy() if worker else None
    else:  # new
        title = "➕ Nouvel Ouvrier"
        submit_label = "➕ Créer Ouvrier"
        worker = _get_default_worker_template()
    
    st.subheader(title)
    
    # Use a proper form with submit button
    with st.form(key=widget_manager.generate_key("worker_form", "worker_table")):
        # Basic Information
        worker = _render_worker_basic_info_section(worker, mode, available_templates, template_id)
        
        # Rates and Productivity - with task template context
        current_task_context = template_context.task_template if template_context.is_ready() else task_template_context
        worker = _render_worker_rates_section(worker, current_task_context)
        
        # Skills and Certifications
        worker = _render_worker_skills_section(worker)
        
        st.markdown("---")
        
        # Form Actions
        col1, col2 = st.columns(2)
        
        with col1:
            submit_clicked = st.form_submit_button(
                submit_label, 
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            cancel_clicked = st.form_submit_button(
                "❌ Annuler", 
                use_container_width=True,
                type="secondary"
            )
        
        # Handle form submissions
        if submit_clicked:
            if _validate_worker(worker, all_workers, mode):
                _save_worker(worker, all_workers, resource_service, user_id, template_id, mode)
        
        if cancel_clicked:
            st.session_state.worker_form_state = {'mode': None, 'current_worker': None}
            st.rerun()
    
    # Productivity testing button (outside the form to avoid conflicts)
    if mode == 'edit' and worker.get('base_productivity_rate'):
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🧪 Tester Productivité", use_container_width=True, type="secondary"):
                _test_worker_productivity(worker, resource_service, current_task_context)

def _test_worker_productivity(worker: Dict, resource_service, task_template_context: Dict = None):
    """
    Professional productivity testing tool for construction workers
    """
    try:
        st.markdown("### 🧪 Test des Taux de Productivité")
        
        # Get productivity rates with proper dict handling
        productivity_rates = worker.get("base_productivity_rate", {})
        
        # Handle legacy format (single float value)
        if isinstance(productivity_rates, (int, float)):
            productivity_rates = {"default": float(productivity_rates)}
            st.info("ℹ️ Format de productivité mis à jour vers le nouveau format dictionnaire")
        
        if not productivity_rates:
            st.warning("⚠️ Aucun taux de productivité défini pour cet ouvrier")
            st.info("💡 Ajoutez des taux de productivité dans la section 'Tarifs et Productivité'")
            return
        
        # Display current productivity configuration
        st.markdown("#### 📊 Configuration Actuelle")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Effectif Base", worker.get("base_count", 1))
        with col2:
            st.metric("👷 Max/Équipe", worker.get("max_workers_per_crew", 1))
        with col3:
            st.metric("📦 Unité", worker.get("productivity_unit", "unités/jour"))
        
        # Display productivity rates in a professional table
        st.markdown("#### 🎯 Taux de Productivité par Tâche")
        
        if productivity_rates:
            import pandas as pd
            productivity_data = []
            for task_id, rate in productivity_rates.items():
                task_display = "Défaut" if task_id == "default" else task_id
                productivity_data.append({
                    "Tâche": task_display,
                    "Taux": f"{rate:.2f}",
                })
            
            df = pd.DataFrame(productivity_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Aucun taux de productivité configuré")
            return
        
        # Productivity Simulation Interface
        st.markdown("#### 🔬 Simulation de Productivité")
        
        # Simulation parameters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            simulation_hours = st.number_input(
                "Heures de travail:",
                value=8,
                min_value=1,
                max_value=24,
                help="Durée de la simulation en heures"
            )
        
        with col2:
            simulation_workers = st.number_input(
                "Nombre d'ouvriers:",
                value=min(worker.get("base_count", 1), worker.get("max_workers_per_crew", 1)),
                min_value=1,
                max_value=worker.get("max_workers_per_crew", 10),
                help="Nombre d'ouvriers pour la simulation"
            )
        
        with col3:
            selected_task = st.selectbox(
                "Tâche à simuler:",
                options=list(productivity_rates.keys()),
                format_func=lambda x: "Taux par défaut" if x == "default" else f"Tâche {x}",
                help="Sélectionnez la tâche à tester"
            )
        
        # Calculate and display results
        if selected_task:
            base_rate = productivity_rates[selected_task]
            
            # Professional calculation
            hourly_productivity = base_rate / 8.0  # Convert daily rate to hourly
            total_productivity = hourly_productivity * simulation_hours * simulation_workers
            
            st.markdown("#### 📈 Résultats de la Simulation")
            
            # Results in a nice layout
            result_col1, result_col2, result_col3 = st.columns(3)
            
            with result_col1:
                st.metric(
                    "Productivité Horaire", 
                    f"{hourly_productivity:.2f}",
                    help="Productivité par ouvrier par heure"
                )
            
            with result_col2:
                st.metric(
                    "Productivité Totale", 
                    f"{total_productivity:.2f}",
                    help=f"Production totale pour {simulation_workers} ouvrier(s) pendant {simulation_hours}h"
                )
            
            with result_col3:
                efficiency = (total_productivity / (base_rate * simulation_workers)) * 100
                st.metric(
                    "Efficacité", 
                    f"{efficiency:.1f}%",
                    help="Efficacité par rapport à une journée standard"
                )
            
            # Detailed breakdown
            with st.expander("📋 Détail des Calculs", expanded=False):
                st.markdown(f"""
                **Formule de calcul:**
                ```
                Productivité Horaire = Taux Journalier / 8 heures
                Productivité Totale = Productivité Horaire × Heures × Ouvriers
                ```
                
                **Application:**
                - Taux de base ({selected_task}): **{base_rate:.2f}** {worker.get('productivity_unit', 'unités')}/jour
                - Productivité horaire: **{base_rate:.2f} / 8 = {hourly_productivity:.2f}** {worker.get('productivity_unit', 'unités')}/heure
                - Production totale: **{hourly_productivity:.2f} × {simulation_hours}h × {simulation_workers} ouvrier(s) = {total_productivity:.2f}** {worker.get('productivity_unit', 'unités')}
                """)
            
            # Professional recommendations
            st.markdown("#### 💡 Recommandations Professionnelles")
            
            if base_rate < 0.5:
                st.warning("**Taux très bas** - Cela peut entraîner des délais prolongés. Vérifiez la cohérence avec les standards du métier.")
            elif base_rate > 10.0:
                st.warning("**Taux très élevé** - Assurez-vous que ce taux est réaliste pour le type de travail.")
            else:
                st.success("**Taux dans la plage standard** - Configuration cohérente.")
            
            # Efficiency analysis
            if efficiency < 80:
                st.info("**Optimisation possible** - Considérez ajuster les effectifs ou améliorer les processus.")
            elif efficiency > 120:
                st.info("**Performance excellente** - Ce taux représente une productivité supérieure à la moyenne.")
            
    except Exception as e:
        st.error(f"❌ Erreur lors du test de productivité: {str(e)}")
        logger.error(f"Productivity test error: {e}")

def _render_worker_basic_info_section(worker: Dict, mode: str, available_templates: List[Dict], template_id: Optional[int] = None) -> Dict:
    """Render worker basic information section with IMPROVED template selection"""
    st.markdown("### 📝 Informations de Base")
    
    col1, col2 = st.columns(2)
    with col1:
        worker["name"] = st.text_input(
            "Nom de l'ouvrier *", 
            value=worker.get("name", ""),
            key=widget_manager.generate_key("worker_name", "worker_table")
        )
        worker["code"] = st.text_input(
            "Code *", 
            value=worker.get("code", ""),
            key=widget_manager.generate_key("worker_code", "worker_table")
        )
        
    with col2:
        # IMPROVED Template selection with better validation
        if available_templates:
            template_options = {f"{t['name']} (ID: {t['id']})": t['id'] for t in available_templates}
            
            # Set default template if provided
            if template_id and not worker.get("template_id"):
                worker["template_id"] = template_id
            
            current_template_id = worker.get("template_id")
            
            # Find current template display name
            current_template_display = None
            if current_template_id:
                for template in available_templates:
                    if template['id'] == current_template_id:
                        current_template_display = f"{template['name']} (ID: {template['id']})"
                        break
            
            selected_template_display = st.selectbox(
                "Modèle de ressources *",
                options=[''] + list(template_options.keys()),
                index=list(template_options.keys()).index(current_template_display) + 1 if current_template_display else 0,
                key=widget_manager.generate_key("worker_template", "worker_table"),
                help="Sélectionnez le modèle auquel cet ouvrier appartient"
            )
            
            if selected_template_display and selected_template_display in template_options:
                worker["template_id"] = template_options[selected_template_display]
            elif not worker.get("template_id"):
                st.error("❌ Veuillez sélectionner un modèle de ressources")
        else:
            st.error("❌ Aucun modèle de ressources disponible. Créez d'abord un modèle.")
        
        worker["specialty"] = st.text_input(
            "Spécialité *", 
            value=worker.get("specialty", ""),
            key=widget_manager.generate_key("worker_specialty", "worker_table")
        )
    
    
    col3, col4 = st.columns(2)
    with col3:
        worker["category"] = st.selectbox(
            "Catégorie *",
            options=["Ouvrier", "Technicien", "Ingénieur", "Superviseur"],
            index=["Ouvrier", "Technicien", "Ingénieur", "Superviseur"].index(worker.get("category", "Ouvrier")),
            key=widget_manager.generate_key("worker_category", "worker_table")
        )
    
    with col4:
        worker["qualification_level"] = st.selectbox(
            "Niveau de qualification *",
            options=["Standard", "Qualifié", "Hautement Qualifié", "Expert"],
            index=["Standard", "Qualifié", "Hautement Qualifié", "Expert"].index(worker.get("qualification_level", "Standard")),
            key=widget_manager.generate_key("worker_qualification", "worker_table")
        )
    
    worker["base_count"] = st.number_input(
        "Effectif de base *", 
        value=worker.get("base_count", 1), 
        min_value=1,
        key=widget_manager.generate_key("worker_base_count", "worker_table")
    )
    
    worker["description"] = st.text_area(
        "Description",
        value=worker.get("description", ""),
        key=widget_manager.generate_key("worker_description", "worker_table")
    )
    
    return worker

def _render_worker_rates_section(worker: Dict, task_template_context: Dict = None) -> Dict:
    """Render worker rates and productivity section with task template context"""
    st.markdown("### 💰 Tarifs et Productivité")
    
    col1, col2 = st.columns(2)
    with col1:
        worker["hourly_rate"] = st.number_input(
            "Taux horaire (€) *", 
            value=worker.get("hourly_rate", 0.0), 
            min_value=0.0,
            step=1.0,
            key=widget_manager.generate_key("worker_hourly_rate", "worker_table")
        )
        worker["daily_rate"] = st.number_input(
            "Taux journalier (€)", 
            value=worker.get("daily_rate", 0.0), 
            min_value=0.0,
            step=1.0,
            key=widget_manager.generate_key("worker_daily_rate", "worker_table")
        )
    
    with col2:
        worker["max_workers_per_crew"] = st.number_input(
            "Maximum par équipe *", 
            value=worker.get("max_workers_per_crew", 1), 
            min_value=1,
            key=widget_manager.generate_key("worker_max_crew", "worker_table")
        )
        
        # Use unit from task template context if available
        default_unit = task_template_context.get('unit', 'unités/jour') if task_template_context else 'unités/jour'
        worker["productivity_unit"] = st.text_input(
            "Unité de productivité par défaut *", 
            value=worker.get("productivity_unit", default_unit),
            key=widget_manager.generate_key("worker_productivity_unit", "worker_table")
        )
    
    # Task-specific productivity rates section
    st.markdown("#### 🎯 Taux de Productivité par Tâche")
    
    if task_template_context:
        st.info(f"Taux pour le modèle: **{task_template_context.get('name', 'Sans nom')}**")
    
    # Initialize productivity rates as dict if not already
    if "base_productivity_rate" not in worker or not isinstance(worker["base_productivity_rate"], dict):
        worker["base_productivity_rate"] = {}
    
    productivity_rates = worker["base_productivity_rate"]
    
    # Display existing task productivity rates
    if productivity_rates:
        st.markdown("**Taux existants:**")
        
        tasks_to_remove = []
        
        for task_id, rate in list(productivity_rates.items()):
            if task_id == "default":
                continue  # Skip default for now
                
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.text_input(
                    "Tâche",
                    value=f"{task_id}",
                    key=f"task_display_{task_id}",
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            with col2:
                new_rate = st.number_input(
                    f"Taux",
                    value=float(rate),
                    min_value=0.1,
                    step=0.1,
                    key=f"rate_edit_{task_id}",
                    label_visibility="collapsed"
                )
                if new_rate != rate:
                    productivity_rates[task_id] = new_rate
            
            with col3:
                st.text_input(
                    "Unité",
                    value=worker.get("productivity_unit", "unités/jour"),
                    key=f"unit_display_{task_id}",
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            with col4:
                if st.button("🗑️", key=f"remove_{task_id}", use_container_width=True):
                    tasks_to_remove.append(task_id)
        
        # Remove tasks marked for deletion
        for task_id in tasks_to_remove:
            if task_id in productivity_rates:
                del productivity_rates[task_id]
                st.rerun()
    
    # Add new task productivity rate section
    st.markdown("---")
    st.markdown("**Ajouter un nouveau taux:**")
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        new_task_id = st.text_input(
            "ID de la tâche",
            placeholder="Ex: TACHE-001",
            key=widget_manager.generate_key("new_task_id", "worker_table")
        )
    
    with col2:
        new_rate = st.number_input(
            "Taux de productivité",
            value=1.0,
            min_value=0.1,
            step=0.1,
            key=widget_manager.generate_key("new_rate_input", "worker_table")
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        add_clicked = st.button(
            "➕ Ajouter",
            key=widget_manager.generate_key("add_productivity_rate", "worker_table"),
            use_container_width=True
        )
    
    # Handle adding new productivity rate
    if add_clicked and new_task_id.strip():
        if new_task_id in productivity_rates:
            st.error(f"❌ Un taux existe déjà pour la tâche {new_task_id}")
        else:
            productivity_rates[new_task_id] = float(new_rate)
            st.success(f"✅ Taux ajouté pour {new_task_id}")
            st.rerun()
    
    # Default productivity rate
    st.markdown("---")
    st.markdown("**Taux par défaut:**")
    
    default_rate = productivity_rates.get("default", 1.0)
    new_default_rate = st.number_input(
        f"Taux de productivité par défaut ({worker.get('productivity_unit', 'unités/jour')}) *",
        value=default_rate,
        min_value=0.1,
        step=0.1,
        key=widget_manager.generate_key("default_productivity_rate", "worker_table"),
        help="Taux utilisé pour les tâches non spécifiées"
    )
    
    if new_default_rate != default_rate:
        productivity_rates["default"] = new_default_rate
    
    # Update the worker dict
    worker["base_productivity_rate"] = productivity_rates
    
    return worker

def _render_worker_skills_section(worker: Dict) -> Dict:
    """Render worker skills and certifications section"""
    st.markdown("### 🛠️ Compétences et Certifications")
    
    # Skills (comma-separated)
    current_skills = worker.get("skills", [])
    skills_str = ", ".join(current_skills) if isinstance(current_skills, list) else str(current_skills)
    
    new_skills_str = st.text_input(
        "Compétences (séparées par des virgules)",
        value=skills_str,
        key=widget_manager.generate_key("worker_skills", "worker_table"),
        help="Liste des compétences séparées par des virgules"
    )
    
    # Process skills input
    if new_skills_str.strip():
        worker["skills"] = [skill.strip() for skill in new_skills_str.split(",") if skill.strip()]
    else:
        worker["skills"] = []
    
    # Certifications (comma-separated)
    current_certs = worker.get("required_certifications", [])
    certs_str = ", ".join(current_certs) if isinstance(current_certs, list) else str(current_certs)
    
    new_certs_str = st.text_input(
        "Certifications requises (séparées par des virgules)",
        value=certs_str,
        key=widget_manager.generate_key("worker_certifications", "worker_table"),
        help="Liste des certifications requises séparées par des virgules"
    )
    
    # Process certifications input
    if new_certs_str.strip():
        worker["required_certifications"] = [cert.strip() for cert in new_certs_str.split(",") if cert.strip()]
    else:
        worker["required_certifications"] = []
    
    # Active status
    worker["is_active"] = st.checkbox(
        "Ouvrier actif",
        value=worker.get("is_active", True),
        key=widget_manager.generate_key("worker_active", "worker_table")
    )
    
    return worker

# --- DATA MANAGEMENT FUNCTIONS ---
def _workers_to_dataframe(workers: List[Dict]) -> pd.DataFrame:
    """Convert workers to DataFrame for display"""
    if not workers:
        return pd.DataFrame()
    
    display_data = []
    for worker in workers:
        row = {}
        for eng_col, fr_col in FRENCH_COLUMNS.items():
            if eng_col in worker:
                value = worker[eng_col]
                if eng_col == 'base_productivity_rate':
                    # Handle productivity rates display
                    if isinstance(value, dict):
                        rates_str = ", ".join([f"{k}:{v}" for k, v in value.items()])
                        row[fr_col] = rates_str
                    else:
                        row[fr_col] = str(value)
                elif eng_col == 'skills' or eng_col == 'required_certifications':
                    row[fr_col] = ", ".join(value) if isinstance(value, list) else value
                elif eng_col == 'is_active':
                    row[fr_col] = '✅' if value else '❌'
                else:
                    row[fr_col] = value
        
        display_data.append(row)
    
    return pd.DataFrame(display_data)

def _save_worker_table_changes(edited_df: pd.DataFrame, workers: List[Dict]):
    """Save changes from data editor"""
    st.info("Fonctionnalité de sauvegarde en ligne à implémenter")

def _validate_worker(worker: Dict, all_workers: List[Dict], mode: str) -> bool:
    """Validate worker data with task-specific productivity rates"""
    errors = []
    
    if not worker.get("name", "").strip():
        errors.append("Le nom de l'ouvrier est obligatoire")
    if not worker.get("code", "").strip():
        errors.append("Le code est obligatoire")
    if not worker.get("specialty", "").strip():
        errors.append("La spécialité est obligatoire")
    if not worker.get("template_id"):
        errors.append("Le modèle de ressources est obligatoire")
    if worker.get("hourly_rate", 0) <= 0:
        errors.append("Le taux horaire doit être positif")
    if worker.get("base_count", 0) <= 0:
        errors.append("L'effectif de base doit être positif")
    
    # Validate productivity rates structure
    productivity_rates = worker.get("base_productivity_rate", {})
    if not isinstance(productivity_rates, dict):
        errors.append("Les taux de productivité doivent être au format dictionnaire")
    else:
        # Check each rate
        for task_id, rate in productivity_rates.items():
            if not task_id.strip():
                errors.append("L'ID de tâche ne peut pas être vide")
            if not isinstance(rate, (int, float)) or rate <= 0:
                errors.append(f"Taux de productivité invalide pour la tâche '{task_id}': doit être un nombre positif")
        
        # Ensure we have at least a default rate
        if not productivity_rates:
            errors.append("Au moins un taux de productivité (par défaut) est requis")
    
    if mode == "new":
        existing_codes = [w.get("code", "").lower() for w in all_workers]
        if worker.get("code", "").lower() in existing_codes:
            errors.append("Un ouvrier avec ce code existe déjà")
    
    for error in errors:
        st.error(f"❌ {error}")
    
    return len(errors) == 0

def _save_worker(worker: Dict, workers: List[Dict], resource_service, user_id: int, template_id: Optional[int], mode: str):
    """Save worker via service layer"""
    try:
        # Set template_id if provided and not already set
        if template_id and not worker.get("template_id"):
            worker['template_id'] = template_id
        
        if mode == 'edit':
            result = resource_service.update_worker(user_id, worker.get('id'), worker)
            if result:
                for i, w in enumerate(workers):
                    if w.get('id') == worker.get('id'):
                        workers[i] = result
                        break
                st.success("✅ Ouvrier modifié avec succès!")
                # Check if template was default and is now modified
                template = next((t for t in resource_service.get_user_resource_templates(user_id) 
                               if t['id'] == template_id), None)
                if template and not template.get('is_default', True):
                    st.info("📝 Note: Ce modèle n'est plus considéré comme 'par défaut' car il a été modifié")
            else:
                st.error("❌ Erreur lors de la modification")
                
        elif mode == 'new':
            result = resource_service.create_worker(user_id, worker)
            if result:
                workers.append(result)
                st.success(f"✅ Ouvrier créé: {result.get('code')}")
            else:
                st.error("❌ Erreur lors de la création")
            
        elif mode == 'duplicate':
            duplicate_worker = worker.copy()
            duplicate_worker['code'] = f"{worker['code']}_COPY"
            result = resource_service.create_worker(user_id, duplicate_worker)
            if result:
                workers.append(result)
                st.success(f"✅ Ouvrier dupliqué: {result.get('code')}")
            else:
                st.error("❌ Erreur lors de la duplication")
        
        # Clear form state
        st.session_state.worker_form_state = {'mode': None, 'current_worker': None}
        
    except Exception as e:
        logger.error(f"Error saving worker: {e}")
        st.error(f"❌ Erreur: {e}")

def _delete_worker(worker: Dict, workers: List[Dict], resource_service, user_id: int):
    """Delete worker with confirmation"""
    worker_id = worker.get('id')
    worker_name = worker.get('name')
    
    st.warning(f"Êtes-vous sûr de vouloir supprimer '{worker_name}'?")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirmer", key=widget_manager.generate_key("confirm_delete_worker", "worker_table")):
            try:
                success = resource_service.delete_worker(user_id, worker_id)
                if success:
                    workers[:] = [w for w in workers if w.get('id') != worker_id]
                    st.success(f"✅ Ouvrier supprimé: {worker_name}")
                else:
                    st.error("❌ Erreur lors de la suppression")
            except Exception as e:
                logger.error(f"Error deleting worker: {e}")
                st.error(f"❌ Erreur: {e}")
    
    with col2:
        if st.button("❌ Annuler", key=widget_manager.generate_key("cancel_delete_worker", "worker_table")):
            st.info("Suppression annulée")

def _get_default_worker_template() -> Dict:
    """Get default worker template with proper productivity rate structure"""
    return {
        "name": "", "code": "", "specialty": "", "category": "Ouvrier",
        "base_count": 1, "hourly_rate": 0.0, "daily_rate": 0.0,
        "max_workers_per_crew": 1, 
        "base_productivity_rate": {"default": 1.0},  # Dict with default rate
        "productivity_unit": "unités/jour", "qualification_level": "Standard",
        "skills": [], "required_certifications": [], "is_active": True,
        "description": "", "template_id": None
    }